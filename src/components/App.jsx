import React from "react"
import PropTypes from "prop-types"
import axios from 'axios';
import Dropzone from 'react-dropzone';

class ImageUploader extends React.Component {
  constructor(props) {
    super(props)
  }

  onDrop(acceptedFiles) {
    // this took a lot of digging into; used this thread for how to get upload to actually work - https://github.com/axios/axios/issues/710#issuecomment-409213073

    acceptedFiles.map((file) => {
      console.log(file)
      const blobFile = new Blob([file]);
      var formData = new FormData();
      formData.append('user_file', blobFile, file.name);

      axios.post('http://localhost:5000/', formData)
        .then(res => {
          const image = res.data;
          //this.props.handleImageUploaded(image)
        })
    })
  }

  render () {
    return (
      <div className="text-center mt-5">
        <Dropzone onDrop={this.onDrop}>
          {({getRootProps, getInputProps}) => (
            <div {...getRootProps()}>
              <input {...getInputProps()} />
              Click me to upload a file!
            </div>
          )}
        </Dropzone>
      </div>
    );
  }
}

export default ImageUploader
