<template>
  <div>
    <div v-if="props.mode === 'review'" class="mb-5">
      <button v-if="!show" class="button--neutral button--smallSquare mt-3" type="button" @click="show = true">
        <span class="fas fa-plus" />
      </button>
      <div v-if="inputValue || show" class="form-group mb-3 mt-4">
        <div class="d-flex">
          <input
            :id="props.id"
            v-model="inputValue"
            type="text"
            class="form-control me-2"
            :placeholder="'Kommentar zum Feld \'' + props.name + '\''"
          />
          <button class="button--danger button--smallSquare" type="button" @click="remove()">
            <span class="fas fa-times" />
          </button>
        </div>
      </div>
    </div>
    <div v-if="props.mode === 'edit' && reviewValue" class="form-comment mb-5">
      Anmerkung: <br />
      {{ reviewValue }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

//  --------------------------------------------------------------------------------------------------------------------
//  models + props
//  --------------------------------------------------------------------------------------------------------------------
const reviewValue = defineModel({ default: '', type: String });

const props = defineProps({
  id: {
    required: true,
    type: String
  },
  mode: {
    default: '',
    type: String
  },
  name: {
    required: true,
    type: String
  }
});

//  --------------------------------------------------------------------------------------------------------------------
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const show = ref(false);
const inputValue = ref(reviewValue);

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const remove = () => {
  show.value = false;
  inputValue.value = '';
};
</script>

<style scoped></style>
