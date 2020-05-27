<template>
  <div class="d-flex justify-content-between steps">
    <div class="step" :class="{'step--is-active': stepIsActive(idx + 1)}" v-for="(step, idx) in steps" @click="setIndex(idx)">
      <img :src="getStepImage(idx + 1)" alt="">
      <div class="step-text">
        {{ step.short }}
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'FormProgress',
    props: {
      steps: {
        type: Array,
        required: true,
        default: () => {
          return []
        }
      },
      active: {
        type: Number,
        default: 0,
        required: false
      }
    },
    methods: {
      getStepImage (idx) {
        if (this.stepIsActive(idx)) {
          return `/static/img/forms/step_${idx}_black.svg`
        }
        return `/static/img/forms/step_${idx}.svg`
      },
      stepIsActive (idx) {
        return idx <= (this.active + 1)
      },
      setIndex (idx) {
        this.$emit('set-index', idx)
      }
    }
  }
</script>

<style scoped>
  .steps {
    position: relative;
  }
  .step {
    flex: 1 0 auto;
    position: relative;
    text-align: center;
    z-index: 1;
    cursor: pointer;
  }
  .step--is-active {
    font-weight: bold;
  }
  .step img {
    width: 40px;
  }
  .step:after,
  .step:before {
    position: absolute;
    display: none;
    z-index: -1;
    top: 50%;
    transform: translateY(-50%);
    content: '';
    width: 50%;
    height: 2px;
    background-color: #231F20;
  }
  .step:not(:last-child):after {
    display: block;
    left: 50%;
  }
  .step:not(:first-child):before {
    display: block;
    left: 0;
  }
  .step-text {
    font-size: 14px;
    width: 150px;
    margin-top: 15px;
    margin-left: auto;
    margin-right: auto;
    display: none;
  }
  @media (min-width: 992px){
    .step-text {
      display: block;
    }
    .step:after,
    .step:before {
      margin-top: -23px;
    }
    .step img {
      width: 60px;
    }
  }
</style>