<template>
  <div class="form-group">
    <label>
      <slot name="label">{{label}}</slot>
    </label>
    <div v-for="option in options">
      <radio
        v-model="selected"
        :name="name"
        :selected-value="option.value"
        type="success"
      >{{ option.text }}</radio>
    </div>
  </div>

</template>

<script>
  import {radio} from 'vue-strap'
  export default {
    components: {
      'radio': radio
    },
    props: ['name', 'value', 'label', 'options'],
    computed: {
      selected: {
        get () {
          return this.value
        },
        set (value) {
          this.$emit('input', value)
        }
      }
    }
  }
</script>
