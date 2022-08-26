document.addEventListener('alpine:init',()=>{
    Alpine.data('collections', () => ({
        collections: [],
        init() {
            console.log('init');
            var socket = io();

            socket.on('connect', function() {
                // socket.emit('my event', {data: 'I\'m connected!'});
                console.log('a user connected');
            });

            //load collections here
        },
        getData() {
            return {
                formData: {
                    name: "",
                    code: "",
                },
                status: false,
                loading: false,
                isError: false,
                modalHeaderText: "",
                modalBodyText: "",                
            }
        },
        submitData(){
            return fetch("/collections", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.formData)
            })
            .then((response) => {
                if(response.status === 201) {
                    this.modalHeaderText = "Congratulations!!!"
                    this.modalBodyText = "You have been successfully added a collection!";
                    this.status = true;
                } else{
                    throw new Error ("Collection registration failed");
                }
            })
        },
    }));

    Alpine.data('specimens',(collectionid)=>({
        specimens: [],
        notifications: [],
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
                console.log('notification received')
                console.log(n)
                console.log(this.specimens)
                fetch("/collections/specimens/1", {
                    method: "GET"
                  }).then((_res) => {
                    _res.json().then(data=>{
                        console.log(data)
                        data.forEach(x => {
                            console.log(x.upload_path);
                            x.upload_path = x.upload_path.replace("src\\torch\\","../");
                            console.log(x.upload_path);
                            if(x.id == n.specimenid){
                                x.progress = n.progress;
                                x.style = "width: " + x.progress + "%"
                            }
                        });
                        this.specimens = data;
                    })
                  });
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
        }
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
