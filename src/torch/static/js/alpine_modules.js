document.addEventListener('alpine:init',()=>{
    Alpine.data('collections', () => ({
        collections: [],
        open: false,
        formData: {
            name: "",
            code: "",
        },
        openPage(collectionid){
            window.open(window.location.href + "/" + collectionid,"_self")
        },
        init() {
            this.open = false;
            var socket = io();

            socket.on('connect', function() {
                // socket.emit('my event', {data: 'I\'m connected!'});
                console.log('a user connected');
            });

            //load collections here
            this.getCollections();
        },
        getCollections(){
            fetch(`/collections/search`, {
                method: "GET"
              }).then((_res) => {
                _res.json().then(data=>{
                    this.collections = data;
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
    }));

    Alpine.data('specimens',(collectionid)=>({
        specimens: [],
        notifications: [],
        open: false,
        openPage(specimenid){
            window.open(window.location.href + "/" + specimenid,"_self")
        },
        init(){
            console.log('specimens init', collectionid);

            this.getSpecimens(collectionid).then(data=>{
                this.specimens = data;
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
                        x.upload_path = x.upload_path.replace("src\\torch\\","../");
                        x.create_date = (new Date(x.create_date)).toLocaleDateString()
                    });
                    return data;
                })
              });
        },
        imageData() {
            return {
              previewUrl: "",
              updatePreview() {
                var reader,
                  files = document.getElementById("thumbnail").files;
          
                reader = new FileReader();
          
                reader.onload = e => {
                  this.previewUrl = e.target.result;
                };
          
                reader.readAsDataURL(files[0]);
              },
              clearPreview() {
                document.getElementById("thumbnail").value = null;
                this.previewUrl = "";
              }
            };
        },
                         
    }));

    // Alpine.data('searchInput', (collectionName) => ({
    //     isOpen: false,
    //     search: "",

    //     get getItems() {

    //         this.getCollections(collectionName).then(data=>{
    //             this.collections = data;
    //         })

    //         const filterItems = this.sourceData.filter((item) => {
                
    //             return item.name.toLowerCase().startsWith(this.search.toLowerCase())
    //             //return item.employee_name.toLowerCase().includes(this.search.toLowerCase())

    //         })

            
    //         if(filterItems.length < this.sourceData.length && filterItems.length > 0) {

    //             this.isOpen = true
    //             return filterItems

    //         } else {

    //           this.isOpen = false

    //         }

    //     },

    //     cleanSearch(e) {
    //       alert(e.target.innerText)
    //       this.search = ""
    //     },
    //     closeSearch() {
    //       this.search = ""
    //       this.isOpen = false
    //     },
    // }))
})
