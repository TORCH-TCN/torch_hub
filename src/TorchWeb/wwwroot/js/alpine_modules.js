document.addEventListener('alpine:init',()=>{
    Alpine.data('collections', () => ({
        collections: [],
        filteredCollections: [],
        open: false,
        formData: {
            name: "",
            code: "",
            collection_folder: "",
        },
        search: "",
        selectedCollection: null,
        selectedCollectionRegexList: [],
        collectionSaved: false,
        openPage(collectionCode){
            window.open(window.location.href + "/" + collectionCode,"_self")
        },
        init() {
            this.open = false;
            let socket = io();

            socket.on('connect', function() {
                console.log('a user connected');
            });

            this.getCollections();
        },
        getCollections(){
            fetch(`/collections/search`, {
                method: "GET"
              }).then((_res) => {
                _res.json().then(data=>{
                    this.selectCollection(data[0]);
                    this.collections = data;
                    this.filteredCollections = data;
                    
                })
              });
        },
        openModal() {
            this.formData.name = "";
            this.formData.code = "";
            this.formData.collection_folder = "";
            this.open = true;
        },
        submitData(){
            if(this.formData.name === "" || this.formData.code === "" || this.formData.collection_folder === "") {
                alert("All the fields are required!")
                return
            }
            fetch("/collections", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.formData)
            })
            .then((response) => {               
                if(response.status === 200) {
                    this.open = false;
                    this.getCollections();
                }else{
                    throw new Error ("Collection registration failed");
                }
            }).catch(error=>{
                console.error(error);
                alert("Collection registration failed");
                throw new Error ("Collection registration failed");
            })
        },
        searchCollection() {
            if (this.search === "") {
                this.filteredCollections = this.collections;
            }
            this.filteredCollections = this.collections.filter((item) => {
                return (item.name
                  .toLowerCase()
                  .includes(this.search.toLowerCase()) || 
                  item.code
                  .toLowerCase()
                  .includes(this.search.toLowerCase()));
            });         
        },
        selectCollection(collection){
            this.selectedCollection = collection
            if (this.selectedCollection.catalog_number_regex == null)
                this.selectedCollectionRegexList = [""]
            else
                this.selectedCollectionRegexList = JSON.parse(this.selectedCollection.catalog_number_regex)
        },
        saveRegex(exp,index){
            this.selectedCollectionRegexList[index] = exp
        },
        addNewRegex(){
            this.selectedCollectionRegexList.push("")
        },
        deleteRegex(index){
            this.selectedCollectionRegexList.splice(index,1)
        },
        saveCollectionSettings(){
            this.selectedCollection.catalog_number_regex = JSON.stringify(this.selectedCollectionRegexList)
                        
            fetch(`/collections`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.selectedCollection)
              }).then((_res) => {
                _res.json().then(data=>{
                   console.log('saveCollectionSettings',data);
                   this.collectionSaved = true;
                })
              });
        },
        deleteCollection(id){
            
            if (confirm("Are you sure you want to remove this collection?") === true) {
                
                fetch(`${id}`, {
                  method: "DELETE",
                  body: JSON.stringify({ collectionId: id }),
                }).then((_res) => {
                    if(_res.status === 200)
                        _res.json().then(data=>{
                            
                            if (data.status === 'ok')
                                this.collections.splice(this.collections.map(x=>x.id).indexOf(id),1);
                            else
                                alert(data.statusText)  
                        })
                    else
                        alert(_res.statusText)  
                }).catch(error=>{
                    console.log(error);
                    alert('Failed to remove the collection');
                });
              }
        },
}));

    Alpine.data('specimens',(collectionId)=>({
        specimens: [],
        filteredSpecimens: [],
        notifications: [],
        open: false,
        search: "",
        onlyErrorToggle: false,
        loading: false,
        fileCounter: 0,
        totalSpecimens: 0,
        pageNumber: 1,
        per_page: 14,
        visiblePages: 3,
        uploadingMessage: "Uploading <span id='fileName'></span>",
        collection: {},

        openPage(specimenId){
            window.open(window.location.href + "/" + specimenId,"_self")
        },

        init(){
            console.log('specimens init');
            
            this.searchSpecimen();

            let socket = io();

            socket.on('connect', function() {
                console.log('a user connected');
            });

            socket.on('notify', (s) => {
                this.updateSpecimenCard(s);
            })

        },
        updateSpecimenCard(s){
            let sIndex = this.specimens.map(x => x.id).indexOf(s.id);

            if (sIndex > -1){
                this.specimens[sIndex].flow_run_state = s.flow_run_state;
                this.specimens[sIndex].failed_task = s.failed_task;
            }
            else{
                if(this.specimens.length === this.per_page) this.specimens.pop();
                
                this.specimens.unshift(s);
                this.updateSpecimenCard(s);
            }
        },
        openModal() {
            
            if (this.collection.workflow != null && this.collection.collection_folder != null){
                if(this.pageNumber !== 1) this.viewPage(1);
                
                this.fileCounter = 0;
                document.getElementById("uploadingMessageContainer").style.display="none";
                this.open = true;
            }
            else{
                alert("You need to select a workflow and folder for this collection. Go to the settings page.")
            }
        },
        searchSpecimen() {
            this.loading = true;
            fetch(`/collections/specimens/${collectionId}?search_string=${this.search}&only_error=${this.onlyErrorToggle}&page=${this.pageNumber}&per_page=${this.per_page}`, {
                method: "GET"
            }).then((_res) => {                
                _res.json().then(data => {
                   
                    this.specimens = data.specimens ? JSON.parse(data.specimens) : [];  
                    this.collection = data.collection ? JSON.parse(data.collection) : {}
                    this.totalSpecimens = data.totalSpecimens;  
                    this.loading = false;            
                                         
                })
            }) 
        },  
        searchStringChanged() {
            this.pageNumber = 1;
            this.searchSpecimen();
        },
        updateCounter(e) {
            this.fileCounter = (this.fileCounter + e);
            if(this.fileCounter === 0){
                this.open = false;
            }
        },
        deleteSpecimen(id){
            
            if (confirm("Are you sure you want to remove this specimen?") === true) {
                
                fetch(`specimen/${id}`, {
                  method: "DELETE"
                }).then((_res) => {
                    if(_res.status === 200)
                        _res.json().then(data=>{
                            
                            if (data.status === 'ok') {
                                this.specimens.splice(this.specimens.map(x=>x.id).indexOf(id),1);   
                                this.searchSpecimen();                                                      
                            } else
                                alert(data.statusText)  
                        })
                    else
                        alert(_res.statusText) 
                        this.open=false;
                }).catch(error=>{
                    console.log(error);
                    alert('Failed to remove the specimen');
                });
              }
        },
        showOnlyError() {
            this.onlyErrorToggle = !this.onlyErrorToggle;
            this.pageNumber = 1;
            this.searchSpecimen();
        },
        pageCount() {
            return Math.ceil(this.totalSpecimens / this.per_page);
        },           
        startPage() {
            if (this.pageNumber === 1) {
              return 1;
            }
            if (this.pageNumber === this.pageCount()) {
              return this.pageCount() - this.visiblePages + 1;
            }
            return this.pageNumber - 1;
        },
        endPage() {
            return Math.min(
              this.startPage() + this.visiblePages - 1,
              this.pageCount()
            );
        },
        pages() {
            const range = [];
            for (let i = this.startPage(); i <= this.endPage(); i += 1) {
              range.push(i);
            }
            console.log("range", range);
            return range;
        },
        viewPage(index) {
            this.pageNumber = index;
            this.searchSpecimen();
        },    
        nextPage() {
            this.pageNumber++;
            this.searchSpecimen();
        },
        prevPage() {
            this.pageNumber--;
            this.searchSpecimen();
        },
        retry(specimen){
            
            let failed_task = specimen.failed_task;
            specimen.failed_task = "Retrying...";
            specimen.flow_run_state = "Retrying"

            fetch(`specimen/retry/${specimen.id}`, {
                method: "POST"
              }).then((_res) => {
                  if(_res.status === 200)
                      _res.json().then(data=>{
                          console.log('result',data);
                      })
                  else{
                    specimen.failed_task = failed_task;
                    specimen.flow_run_state = "Failed"
                    alert(_res.statusText)
                  }
                      
              }).catch(error=>{
                  specimen.failed_task = failed_task;
                  specimen.flow_run_state = "Failed"
                  alert('Something wrong happened:' + error);
              });
        },
        deleteTransferredSpecimens(){
            
            if (confirm("Are you sure you want to remove the transferred specimens? This will delete all related specimen files.") === true) {
                
                fetch(`transferred-specimens/${this.collection.id}`, {
                  method: "DELETE"
                }).then((_res) => {
                    console.log("res alpine:", _res)
                    if(_res.status === 200)
                        _res.json().then(data=>{
                            
                            if (data.status === 'ok') {
                                this.searchSpecimen();                                                      
                            } else
                                alert(data.statusText)  
                        })
                    else
                        alert(_res.statusText)                         
                }).catch(error=>{
                    console.log(error);
                    alert('Failed to remove the transferred specimens');
                });
              }
        },
        downloadCSV(){                         
            fetch(`export-csv/${this.collection.id}`, {
                method: "GET"
            }).then( res => res.blob() )
                .then( blob => {
                    let file = window.URL.createObjectURL(blob);
                    window.location.assign(file);
            });
        }
    }));
})
