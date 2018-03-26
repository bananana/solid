$(document).ready(function () {
    var input = document.querySelector('#images');
    var preview = document.querySelector('#preview');

    input.addEventListener('change', updateImageDisplay);
    function updateImageDisplay() {
        while(preview.firstChild) {
            preview.removChild(preview.firstChild);
        }

        var curFiles = input.files;
        if(curFiles.length > 0) {
            var list = document.createElement('ul');
            list.className = "u-remove-margin-bottom";
            preview.appendChild(list);
            for(var i = 0; i < curFiles.length; i++) {
                var listItem = document.createElement('li');
                if(validFileType(curFiles[i])) {
                    var image = document.createElement('img');
                    image.src = window.URL.createObjectURL(curFiles[i]);
                    listItem.appendChild(image);
                } else {
                    var para = document.createElement('p');
                    para.innerHTML = curFiles[i].name + '<br><strong>Not a valid file type.</strong>';
                    listItem.className = "error";
                    listItem.appendChild(para);
                }
                list.appendChild(listItem);
            }
        }
    }

    var fileTypes = [
        'image/jpeg',
        'image/gif',
        'image/png'
    ]
    function validFileType(file) {
        for(var i = 0; i < fileTypes.length; i++) {
            if(file.type === fileTypes[i]) {
                return true;
            }
        }
        return false;
    }
});
