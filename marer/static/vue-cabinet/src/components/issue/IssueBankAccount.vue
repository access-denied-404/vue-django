<template>
  <tr>
    <td class="h6">
      {{ id }}
      <bs-input :value="name"></bs-input>
    </td>
    <td class="h6">
      <bs-input :value="bik"></bs-input>
    </td>
    <td class="h6">
      <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
        <span class="glyphicon glyphicon-remove text-danger"></span>
      </button>
    </td>
  </tr>
</template>
<script>
  import input from 'vue-strap'

  export default {
    name: 'issue_bank_account',
    components: {
      'bs-input': input
    },
    props: ['bank'],
    data () {
      return {
      }
    },
    mounted: function () {
    },
    computed: {
    },
    methods: {
    }
  }
</script>


