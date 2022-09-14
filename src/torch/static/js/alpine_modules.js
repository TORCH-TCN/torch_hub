document.addEventListener('alpine:init',()=>{
    Alpine.data('collections', () => ({
        collections: [],
        filteredCollections: [],
        open: false,
        formData: {
            name: "",
            code: "",
        },
        search: "",
        selectedCollection: null,
        collectionSaved: false,
        openPage(collectioncode){
            window.open(window.location.href + "/" + collectioncode,"_self")
        },
        init() {
            this.open = false;
            var socket = io();

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
                    this.selectedCollection = data[0];
                    this.collections = data;
                    this.filteredCollections = data;
                    
                })
              });
        },
        submitData(e){
            return fetch("/collections", {
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
        },
        saveCollectionSettings(){
            console.log('saveCollectionSettings',this.selectedCollection);
            
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
        }
    }));

    Alpine.data('specimens',(collectionid)=>({
        specimens: [],
        filteredSpecimens: [],
        notifications: [],
        open: false,
        search: "",
        openPage(specimenid){
            window.open(window.location.href + "/" + specimenid,"_self")
        },
        init(){
            console.log('specimens init', collectionid);

            this.getSpecimens(collectionid).then(data=>{
                this.specimens = data;
                this.filteredSpecimens = data;
            })

            var socket = io();

            socket.on('connect', function() {
                console.log('a user connected');
            });

            socket.on('notify', (n) => {
                this.getSpecimens(collectionid).then(data=>{
                    data.forEach(x => {
                        if(x.id == n.specimenid){
                            x.progress = n.progress;
                            x.style = "width: " + x.progress + "%"
                        }
                    });
                    this.specimens = data;
                })

               
            })
        },
        getSpecimens(collectionid){
            return fetch(`/collections/specimens/${collectionid}`, {
                method: "GET"
              }).then((_res) => {
                return _res.json().then(data=>{
                    
                    data.forEach(x => {
                        x.upload_path = x.upload_path.replace("torch\\","../");
                        x.create_date = (new Date(x.create_date)).toLocaleDateString()
                    });
                    return data;
                })
              });
        },
        searchSpecimen() {
            fetch(`/collections/specimens/${collectionid}?searchString=${this.search}`, {
                method: "GET"
            }).then((_res) => {                
                _res.json().then(data => {
                    this.specimens = data;                  
                })
            }) 
        },                         
    }));

})
