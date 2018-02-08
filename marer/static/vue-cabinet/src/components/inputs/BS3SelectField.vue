<template>
  <div class="form-group">
    <label>{{label}}</label>
    <select v-model="selected" :name="name" class="form-control">
      <option v-for="option in options" v-bind:value="option.value">
        {{ option.text }}

      </option>
    </select>
  </div>

</template>

<script>
  export default {
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
