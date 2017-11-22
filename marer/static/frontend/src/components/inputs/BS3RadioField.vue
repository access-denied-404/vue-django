<template>
  <div v-if="cols > 0">
    <div class="form-group">
      <label>
        <slot name="label">{{label}}</slot>
      </label>
      <div class="row">
        <div v-for="option in options" :class="colClass">
          <radio v-model="selected" :name="name" :selected-value="option.value" type="primary" :button="button">{{ option.text }}</radio>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <label>
      <slot name="label">{{label}}</slot>
    </label>
    <div>
      <radio v-for="option in options" v-model="selected" :name="name" :selected-value="option.value" type="primary" :button="button">{{ option.text }}</radio>
    </div>
  </div>
</template>

<script>
  import {radio} from 'vue-strap'
  export default {
    components: {
      'radio': radio
    },
    props: ['name', 'value', 'label', 'options', 'cols', 'button'],
    computed: {
      selected: {
        get () {
          return this.value
        },
        set (value) {
          this.$emit('input', value)
        }
      },
      colClass: {
        get () {
          if (this.cols) {
            // available values: 1, 2, 3, 4, 6, 12
            let colSize = Math.floor(12 / this.cols)
            if (colSize < 1) colSize = 1
            if (colSize > 12) colSize = 12
            return 'col-sm-' + colSize.toString()
          } else {
            return 'col-sm-12'
          }
        }
      }
    }
  }
</script>

<style scoped="default">
  .radio {
    margin: 2px 0;
  }
</style>
