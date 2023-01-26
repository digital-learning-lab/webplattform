<template>
  <div class="form-group">
      <label  :for="id" class="mb-2 w-100"><span class="icon--dlt mr-3" :class="iconClass" v-if="icon"></span> {{ label }}:<span v-if="required">*</span></label>
      <button class="button--neutral button--smallSquare button--help ml-1 float-right" type="button" data-toggle="tooltip" data-placement="top" :title="helpText" v-if="helpText"></button>
    <div class="form__links-input">
      <div class="d-flex align-items-baseline ">
        <select class="form-control mr-3" name="types" v-model="complianceLevel" @change="updateText">
          <option value="compliant">Erfüllt</option>
          <option value="not_compliant">Nicht erfüllt</option>
          <option value="unknown">Unbekannt</option>
        </select>
        <input type="text" class="form-control mr-3" :class="{'form__field--error': error}" :id="id" placeholder="Anmerkungen" v-model="complianceText" :readonly="readonly">
      </div>
    </div>
    <app-review-input :mode="review ? 'review' : 'edit'" :id="'id'+-review" :name="label" :reviewValue.sync="ownReviewValue"></app-review-input>
  </div>
</template>

<script>
  import ReviewInput from './ReviewInput.vue'
  import { reviewMixin } from '../mixins/reviewMixin'
  export default {
    name: 'DataProtectionInput',
    components: {
      'AppReviewInput': ReviewInput
    },
    mixins: [reviewMixin],
    props: {
      id: {
        type: String,
        default: '',
        required: true
      },
      required: {
        type: Boolean,
        default: false,
        required: false
      },
      label: {
        type: String,
        default: '',
        required: true
      },
      icon: {
        type: String,
        default: '',
        required: false
      },
      error: {
        type: Boolean,
        default: false,
        required: false
      },
      helpText: {
        type: String,
        default: '',
        required: false
      },
      readonly: {
        type: Boolean,
        default: false,
        required: false
      }
    },
    data () {
      return {
        complianceLevel: 'unknown',
        complianceText: '',
        defaultTextCompliant: '',
        defaultTextNotCompliant: '',
        defaultTextUknown: ''
      }
    },
    computed: {
      iconClass () {
        if (this.icon) {
          const icon = this.icon ? 'icon-' + this.icon : ''
          if (this.complianceLevel === 'compliant') {
            return icon + '--green'
          } else if (this.complianceLevel === 'not_compliant') {
            return icon + '--red'
          } else {
            return icon + '--grey'
          }
        }
        return ''
      }
    },
    methods: {
      isDefaultText(s) {
        return s === this.defaultTextCompliant || s === this.defaultTextNotCompliant || s === this.defaultTextUknown || s === ''
      },
      updateText(event) {
        if (event.target.value === 'compliant') {
          if (this.isDefaultText(this.complianceText)) {
            this.complianceText = this.defaultTextCompliant
          }
        } else if (event.target.value === 'not_compliant') {
          if (this.isDefaultText(this.complianceText)) {
            this.complianceText = this.defaultTextNotCompliant
          }
        } else {
          if (this.isDefaultText(this.complianceText)) {
            this.complianceText = this.defaultTextUknown
          }
        }
      }
    },
    created () {
      this.defaultTextCompliant = window.compliance[this.id].compliant;
      this.defaultTextNotCompliant = window.compliance[this.id].not_compliant;
      this.defaultTextUknown = window.compliance[this.id].unknown;
    },
    watch: {
    }
  }
</script>

<style scoped>

</style>