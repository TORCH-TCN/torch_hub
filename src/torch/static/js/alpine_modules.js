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

    Alpine.data('specimens',()=>({
        specimens: [],
        notifications: [],
        init(){
            console.log('specimens init');

            var socket = io();

            socket.on('connect', function() {
                // socket.emit('my event', {data: 'I\'m connected!'});
                console.log('a user connected');
            });

            socket.on('notify', function(n){
                console.log('notification received')
                console.log(n)
            })
        }
    }));
})
