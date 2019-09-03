<template>
  <div>
    <label for="dropzone" :label="label"></label>
    <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions" v-on:removedfile="removeFileFromList" @vdropzone-success="addFileToList" :include-styling="true"></vue-dropzone>
    <ul class="list-unstyled">
      <li v-for="file in fileList" class="file-list__item">
        <a :href="file.url">{{ file.title }}</a>
        <a href="#" @click="removeFile($event, file)" class="float-right">Löschen</a>
      </li>
    </ul>
  </div>
</template>

<script>
  import vue2Dropzone from 'vue2-dropzone'
  import { axiosMixin } from '../mixins/axiosMixin'

  export default {
    name: 'Dropzone',
    components: {
      vueDropzone: vue2Dropzone
    },
    mixins: [axiosMixin],
    props: {
      slug: {
        type: String,
        default: '',
        required: true
      },
      label: {
        type: String,
        default: '',
        required: true
      },
      files: {
        type: Array,
        default: () => {
          return []
        },
        required: false
      }
    },
    data () {
      return {
        fileList: []
      }
    },
    methods: {
      removeFile (e, file) {
        e.preventDefault()
        this.removeFileFromList(file)
      },
      removeFileFromList (file) {
        const axiosInstance = this.getAxiosInstance()
        axiosInstance.delete(
          '/api/inhalt-bearbeiten/' + this.slug + '/file-remove/' + file.id
        ).then(res => {
          const idx = this.fileList.indexOf(file)
          this.fileList.splice(idx, 1)
        }).catch(err => {
          console.log(err)
        })
      },
      addFileToList (file) {
        this.fileList.push(JSON.parse(file.xhr.response))
      }
    },
    computed: {
      dropzoneOptions () {
        return {
          url: '/api/inhalt-bearbeiten/' + this.slug + '/file-upload',
          method: 'PUT',
          headers: {
            'X-CSRFToken': window.dllData.csrfToken
          },
          acceptedFiles:
            '.pdf,.docx,.doc,.pptx,.ppt,.xls,.xlsx,.odt,.odp,.ods,.wav,.mp3,.zip,.png,.jpg,.jpeg,.gif'
          ,
          dictDefaultMessage: 'Dateien hier hinziehen',
          dictFallbackMessage: 'Ihr Browser ist nicht für den Dateiupload unterstützt.',
          dictFallbackText: null,
          dictFileTooBig: 'Die Datei ist leider zu groß. Bitte wählen Sie eine kleinere Datei.',
          dictInvalidFileType: 'Ungültiger Dateityp.',
          dictResponseError: 'Ungültige Antwort: {{ statusCode }}.',
          dictCancelUpload: 'Upload abbrechen',
          dictUploadCanceled: 'Upload abgebrochen',
          dictCancelUploadConfirmation: 'Upload wurde abgebrochen',
          dictRemoveFile: 'Datei entfernen',
          dictRemoveFileConfirmation: 'Datei wurde entfernt.',
          dictMaxFilesExceeded: 'Maximale Datei-Anzahl erreicht.'
        }
      }
    },
    created () {
      this.fileList = this.files
    },
    watch: {
      files (newValue) {
        this.fileList = newValue
      }
    }
  }
</script>

<style scoped>
</style>