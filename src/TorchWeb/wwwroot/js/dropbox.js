Dropzone.options.dropbox = {
  uploadMultiple: true,
  parallelUploads: 1,
  paramName: (n) => 'file',

  init: function() {
    this.on("addedfile", file => {
      console.log("A file has been added");
      let element = document.getElementById("fileName");
      if (element) {
        element.innerHTML = file.name;
        document.getElementById("uploadingMessageContainer").style.display="";
      }
      const incrementCounter = new CustomEvent('increment-counter');
      window.dispatchEvent(incrementCounter);
    });
    this.on("complete", file => {
      console.log('uploaded');
      //this.removeFile(file);
      const decrementCounter = new CustomEvent('decrement-counter');
      window.dispatchEvent(decrementCounter);
    });
    this.on("successmultiple", () => {
      console.log('successmultiple');
      // var closeModal = new CustomEvent('close-modal');
      // window.dispatchEvent(closeModal);
    });
  }
};
