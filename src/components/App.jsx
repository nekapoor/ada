import React from "react";
import PropTypes from "prop-types";
import axios from 'axios';
import Dropzone from 'react-dropzone';
import RegionSelect from 'react-region-select';

class ImageUploader extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      regions: [], 
      imageData: [],
      image_url: ''
    }

    this.onDrop = this.onDrop.bind(this)
    this.onChange = this.onChange.bind(this);
    this.handleButtonClick = this.handleButtonClick.bind(this);
    this.regionRenderer = this.regionRenderer.bind(this);

  }

  onDrop(acceptedFiles) {
    // this took a lot of digging into; used this thread for how to get upload to actually work - https://github.com/axios/axios/issues/710#issuecomment-409213073

    acceptedFiles.map((file) => {
      console.log(file)
      const blobFile = new Blob([file]);
      var formData = new FormData();
      formData.append('user_file', blobFile, file.name);

      axios.post(process.env.HOST, formData)
        .then(res => {
          console.log(res)

          this.setState({
            image_url: res.data
          }) 
        })
    })
  }

  handleButtonClick() {
    const rois = this.state.regions.map(region => region.data)

    if (rois === undefined || rois.length == 0) {
      console.log('No selection made')
    } else {
      console.log(rois)

      const formData = {
        rois: rois,
        url: `${process.env.HOST}/static/${this.state.image_url}`
      }

      console.log(formData)

      axios.post(`${process.env.HOST}/images/roi`, formData)
        .then((res) => {
          console.log('GOT HERE HANDLE BUTTON CLICK')
          console.log(res)
          this.setState({ imageData: res.data.data })
          console.log(this.state.imageData)
          console.log(this.state.imageData[0].index)
        })
        .catch(console.log)
    }

  }
  
  regionRenderer (regionProps) {
    if (!regionProps.isChanging) {
      return (
        <div style={{size: '16px', color: '#ff0000'}} >
          {regionProps.index}
        </div>
      );
    }
  }

  onChange(regions) {
    const rawImage = document.getElementById('jpg-image')

    const { width, height } = rawImage
    const actualWidth = rawImage.naturalWidth
    const actualHeight = rawImage.naturalHeight

    regions.map(region => {
      let data = region.data
      const h = region.height / 100 * actualHeight
      const w = region.width / 100 * actualWidth

      let x1 = region.x / 100 * actualWidth
      let y1 = region.y / 100 * actualHeight
      let x2 = x1 + w
      let y2 = y1 + h

      data.x1 = x1
      data.x2 = x2
      data.y1 = y1
      data.y2 = y2
      data.label = data.index
    })

    this.setState({
      regions: regions
    });

    console.log(this.state)
  }


  render () {
    return (
      <div className="container">
        <div className="row mt-5 mb-5">
          <div className="col-md-12">
            <Dropzone onDrop={this.onDrop}>
              {({getRootProps, getInputProps}) => (
                <div {...getRootProps()}>
                  <input {...getInputProps()} />

                  <div className="text-center">Click me to upload a raw image file!</div>
                </div>
              )}
            </Dropzone>
            <hr />

          </div>
        </div>
        <div className="row">
          <div className="col-md-5">


            { //Check if message failed
              (this.state.image_url == '')
                ? <div> Upload a raw file above and we'll convert it to a jpg and render it here </div> 
                : (<RegionSelect
                      maxRegions={100}
                      regions={this.state.regions}
                      onChange={this.onChange}
                      regionRenderer={this.regionRenderer}
                    >
                      <img src={`${process.env.HOST}/static/${this.state.image_url}`} id='jpg-image' width="100%" />
                    </RegionSelect>
                  )
            }
          </div>
          <div className="col-md-7">
            <div className="table-responsive">
              <table className="table" id="image-data">
                <thead>
                  <tr>
                    <th>Label</th>
                    <th>X</th>
                    <th>Y</th>
                    <th>Z</th>
                    <th>R</th>
                    <th>G</th>
                    <th>B</th>
                  </tr>
                </thead>

                <tbody>
                  {this.state.imageData && this.state.imageData.map(data => (
                    <tr key={data.label}>
                      <td>{data.label}</td>
                      <td>{data.xyz.x}</td>
                      <td>{data.xyz.y}</td>
                      <td>{data.xyz.z}</td>
                      <td>{data.srgb.r}</td>
                      <td>{data.srgb.g}</td>
                      <td>{data.srgb.b}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col-md-12 mt-4">
            <button className="btn btn-primary btn-block" onClick={this.handleButtonClick}>Retrieve Selected Region Data</button>
          </div>
        </div>
    </div>
    );
  }
}

export default ImageUploader
