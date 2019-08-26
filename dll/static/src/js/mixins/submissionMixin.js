import axios from 'axios'

import TextInput from '../components/TextInput.vue'
import TextArea from '../components/TextArea.vue'
import Dropdown from '../components/Dropdown.vue'
import FileInput from '../components/FileInput.vue'
import Select from '../components/Select.vue'
import RangeInput from '../components/RangeInput.vue'
import LinksInput from '../components/LinksInput.vue'
import ListInput from '../components/ListInput.vue'

export const submissionMixin = {
  components: {
    'AppDropdown': Dropdown,
    'AppFileInput': FileInput,
    'AppTextInput': TextInput,
    'AppTextArea': TextArea,
    'AppRangeInput': RangeInput,
    'AppLinksInput': LinksInput,
    'AppListInput': ListInput,
    'AppSelect': Select
  },
  data () {
    return {
      mode: 'create',
      errors: [],
      saved: false,
      data: {},
      loading: false,
      previewImage: null,
      imageOptions: [
        {label: 'Ja', value: 'y'},
        {label: 'Nein', value: 'n'},
      ],
      requiredFields: [
        {field: 'name', title: 'Titel'},
        {field: 'teaser', title: 'Teaser'},
        {field: 'description', title: 'Detaillierte Beschreibung'},
        {field: 'competences', title: 'Kompetenzen in der digitalen Welt'}
      ],
      licenseOptions: [
        {value: null, label:'----------'},
        {value: 1, label:'CC0'},
        {value: 2, label:'CC BY'},
        {value: 5, label:'CC BY-NC'},
        {value: 7, label:'CC BY-NC-ND'},
        {value: 6, label:'CC BY-NC-SA'},
        {value: 4, label:'CC BY-ND'},
        {value: 3, label:'CC BY-SA'}
      ],
    }
  },
  methods: {
    showDeleteWarning () {
      this.mode = 'delete'
    },
    deleteContent () {
      const axios = this.getAxiosInstance()
      axios.delete('/api/inhalt-bearbeiten/' + this.data.slug)
        .then(res => {
          document.location = '/meine-inhalte'
        })
    },
    getHelpText (fieldName) {
      if (fieldName && this.data.help_texts) {
        return this.data.help_texts[fieldName]
      }
      return null
    },
    getAxiosInstance () {
      const axiosInstance = axios.create({
        headers: {
          'X-CSRFToken': window.dllData.csrfToken
        }
      })
      return axiosInstance
    },
    createContent () {
      this.errors = []
      const axiosInstance = this.getAxiosInstance()
      this.loading = true
      axiosInstance.post('/api/inhalt-bearbeiten/', {
        ...this.data,
        resourcetype: this.resourceType
      }).then(res => {
        this.loading = false
        this.mode = 'edit'
        this.data = res.data
        this.data.author = window.dllData.authorName
      }).catch(err => {
        this.loading = false
        if (err.response.status === 400) {
          for (let field in err.response.data) {
            for (let i = 0; i < err.response.data[field].length; i++) {
              this.errors.push(err.response.data[field][i])
            }
          }
        }
      })
    },
    updateContent () {
      this.validate()
      if (this.errors.length) {
        return
      }
      if (this.data.literatureLinks && this.data.mediaLinks) {
        this.data.contentlink_set = this.data.mediaLinks.concat(this.data.literatureLinks)
      } else if (this.data.mediaLinks) {
        this.data.contentlink_set = this.data.mediaLinks
      } else if(this.data.literatureLinks) {
        this.data.contentlink_set = this.data.literatureLinks
      }
      this.data.related_content = this.data.tools.concat(this.data.trends.concat(this.data.teaching_modules))
      const axiosInstance = this.getAxiosInstance()
      this.loading = true
      if (this.previewImage) {
        let formData = new FormData()

        formData.append('image', this.previewImage, this.previewImage.name)
        axiosInstance.put('/api/inhalt-bearbeiten/' + this.data.slug + '/vorschau-bild', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then(res => {

        }).catch(err => {
          if (err.response.status === 400) {
            for (let i = 0; i < err.response.data.length; i++) {
              this.errors.push(err.response.data[i])
            }
          }
        })
      }

      axiosInstance.put('/api/inhalt-bearbeiten/' + this.data.slug + '/', {
        ...this.data,
        resourcetype: this.resourceType
      }).then(res => {
        this.loading = false
        this.saved = true
        this.mode = 'edit'
        setTimeout(() => {
          this.saved = false
        }, 5000)
      }).catch(err => {
        this.loading = false
        if (err.response.status === 400) {
          for (let i = 0; i < err.response.data.length; i++) {
            this.errors.push(err.response.data[i])
          }
        }
      })
    },
    validate () {
      this.errors = []
      for (let i = 0; i < this.requiredFields.length; i++) {
        if (!this.data[this.requiredFields[i].field]) {
          this.errors.push('Bitte füllen Sie das Pflichtfeld \'' + this.requiredFields[i].title + '\' aus.')
        }
      }
    },
    goToPreview () {
      document.location = this.data.preview_url
    }
  },
  created () {
    if (window.dllData) {
      this.mode = window.dllData.mode || 'create'
      if (this.mode === 'edit') {
        this.data = window.dllData.module
        this.data.mediaLinks = this.data.contentlink_set.filter(link => link.type === 'video' || link.type === 'audio')
        this.data.literatureLinks = this.data.contentlink_set.filter(link => link.type === 'href' || link.type === 'literature')
      }
      this.data.author = window.dllData.authorName
    }
  }
}