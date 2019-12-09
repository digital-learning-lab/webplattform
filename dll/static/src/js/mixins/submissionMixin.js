import $ from 'jquery'
import Vue from 'vue'

import TextInput from '../components/TextInput.vue'
import TextArea from '../components/TextArea.vue'
import Dropdown from '../components/Dropdown.vue'
import FileInput from '../components/FileInput.vue'
import Select from '../components/Select.vue'
import RangeInput from '../components/RangeInput.vue'
import LinksInput from '../components/LinksInput.vue'
import ListInput from '../components/ListInput.vue'
import PendingCoAuthors from '../components/PendingCoAuthors.vue'
import { axiosMixin } from './axiosMixin'
import LinkInput from '../components/LinkInput.vue'

export const submissionMixin = {
  components: {
    'AppDropdown': Dropdown,
    'AppFileInput': FileInput,
    'AppTextInput': TextInput,
    'AppTextArea': TextArea,
    'AppRangeInput': RangeInput,
    'AppLinksInput': LinksInput,
    'AppLinkInput': LinkInput,
    'AppListInput': ListInput,
    'AppSelect': Select,
    'AppPendingCoAuthors': PendingCoAuthors
  },
  mixins: [axiosMixin],
  data () {
    return {
      mode: 'create',
      errors: [],
      saved: false,
      data: {},
      reviewValue: {},
      canDelete: false,
      loading: false,
      previewImage: null,
      imageHintText: 'Mit dem Upload bestätigen Sie, dass Sie der Inhaber des vollumfänglichen Nutzungsrechts sind und Ihnen beliebige Veröffentlichungen, Bearbeitungen und Unterlizenzierungen dieses Werkes gestattet sind.',
      imageOptions: [
        {label: 'Ja', value: 'y'},
        {label: 'Nein', value: 'n'},
      ],
      requiredFields: [
        {field: 'name', title: 'Titel'},
        {field: 'teaser', title: 'Teaser'},
        {field: 'image', title: 'Anzeigebild'},
        {field: 'competences', title: 'Kompetenzen in der digitalen Welt'},
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
      errorFields: []
    }
  },
  methods: {
    initToolTips () {
      $('[data-toggle="tooltip"]').tooltip({
        trigger: 'manual'
      }).click(e => {
        $(e.target).tooltip('toggle')
      }).on('show.bs.tooltip', () => {
        $('[data-toggle="tooltip"]').tooltip('hide')
      })
    },
    updateReview () {
      const axios = this.getAxiosInstance()
      this.loading = true
      return axios.put('/api/review/' + this.data.slug + '/', {
        json_data: this.reviewValue
      })
        .then(res => {
          this.loading = false
          this.saved = true
          setTimeout(() => {
            this.saved = false
          }, 5000)
        })
        .catch(err => {
          this.loading = false
        })
    },
    approveContent () {
      this.updateReview()
        .then(res => {
          const axios = this.getAxiosInstance()
          this.loading = true
          axios.post('/api/review/' + this.data.slug + '/approve')
            .then(res => {
              this.loading = false
              document.location = '/review-inhalte'
            })
            .catch(err => {
              this.loading = false
            })
        })
    },
    declineContent () {
      this.updateReview()
        .then(res => {
          const axios = this.getAxiosInstance()
          this.loading = true
          axios.post('/api/review/' + this.data.slug + '/decline')
            .then(res => {
              document.location = '/review-inhalte'
              this.loading = false
            })
            .catch(err => {
              this.loading = false
            })
        })
    },
    submitContent () {
      this.errorFields = []
      this.updateContent().then(res => {
        this.validate()
        if (this.errors.length) {
          throw Error('Form is not valid!')
        }
        this.loading = true
        const axios = this.getAxiosInstance()
        axios.post('/api/inhalt-einreichen/' + this.data.slug)
          .then(res => {
            this.data.submitted = true
            this.loading = false
          })
          .catch(err => {
            this.loading = false
          })
      })
    },
    showDeleteWarning () {
      this.mode = 'delete'
    },
    deleteContent () {
      this.loading
      const axios = this.getAxiosInstance()
      axios.delete('/api/inhalt-bearbeiten/' + this.data.slug)
        .then(res => {
          this.loading = false
          document.location = '/meine-inhalte'
        })
    },
    getHelpText (fieldName) {
      if (fieldName && this.data.help_texts) {
        return this.data.help_texts[fieldName] || '.'
      }
      return null
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
        window.history.pushState('Content created', '', document.location.pathname + this.data.slug)
        Vue.nextTick(() => {
          this.initToolTips()
        })
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

        formData.append('file', this.previewImage, this.previewImage.name)
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
      this.errors = []
      this.errorFields = []
      return axiosInstance.put('/api/inhalt-bearbeiten/' + this.data.slug + '/', {
        ...this.data,
        resourcetype: this.resourceType
      }).then(res => {
        this.loading = false
        this.saved = true
        this.mode = 'edit'
        this.setContent(res.data)
        setTimeout(() => {
          this.saved = false
        }, 5000)
      }).catch(err => {
        this.loading = false
        if (err.response.status === 400) {
          for (let field in err.response.data) {
            for (let i = 0; i < err.response.data[field].length; i++) {
              this.errors.push(err.response.data[field][i])
              this.errorFields.push(field)
              console.log(field)
            }
          }
        }
      })
    },
    validate () {
      this.errors = []
      for (let i = 0; i < this.requiredFields.length; i++) {
        if (this.requiredFields[i].field === 'image' && !this.data.image) {
          if (!this.previewImage) {
            this.errors.push('Bitte füllen Sie das Pflichtfeld \'' + this.requiredFields[i].title + '\' aus.')
            this.errorFields.push(this.requiredFields[i].field)
          }
          continue
        }
        if (!this.data[this.requiredFields[i].field] ||
          (Array.isArray(this.data[this.requiredFields[i].field]) && !this.data[this.requiredFields[i].field].length)) {
          this.errors.push('Bitte füllen Sie das Pflichtfeld \'' + this.requiredFields[i].title + '\' aus.')
          this.errorFields.push(this.requiredFields[i].field)
        }
        if (typeof this.data[this.requiredFields[i].field] === 'object') {
          console.log(this.requiredFields[i].field)
          for (let key in this.data[this.requiredFields[i].field]) {
            console.log(key)
            if (!this.data[this.requiredFields[i].field][key]) {
              console.log(this.data[this.requiredFields[i].field][key])
              this.errors.push('Bitte füllen Sie das Pflichtfeld \'' + this.requiredFields[i].title + '\' komplett aus.')
              this.errorFields.push(this.requiredFields[i].field)
              break
            }
          }
        }
      }
    },
    goToPreview () {
      this.updateContent().then(res => {
        document.location = this.data.preview_url
      })
    },
    setContent (content) {
      this.data = content
      this.data.mediaLinks = this.data.contentlink_set.filter(link => link.type === 'video' || link.type === 'audio')
      this.data.literatureLinks = this.data.contentlink_set.filter(link => link.type === 'href' || link.type === 'literature')
      this.data.author = this.data.author.username
    }
  },
  computed: {
     readonly () {
      return this.data.submitted || this.mode === 'review'
    },
    review () {
      return this.mode === 'review'
    }
  },
  created () {
    if (window.dllData) {
      this.mode = window.dllData.mode || 'create'
      this.canDelete = window.dllData.canDelete || false
      if (this.mode === 'edit' || this.mode === 'review') {
        this.setContent(window.dllData.module)
        if (window.dllData.module.review) {
          this.reviewValue = window.dllData.module.review.json_data
        }
      }
      this.data.author = window.dllData.authorName
    }
  },
  mounted () {
    this.initToolTips()
  }
}