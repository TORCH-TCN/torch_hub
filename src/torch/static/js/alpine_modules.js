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
})
