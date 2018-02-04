<template>
  <div id="app-root">

  </div>
</template>

<script>
  import {input} from 'vue-strap'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import jQuery from 'jquery'
  require('suggestions-jquery')
  export default {
    name: 'app',
    props: ['csrf', 'products', 'token'],
    components: {
      'bs-input': input,
      'bs3-select-field': BS3SelectField
    },
    data () {
      var regData = JSON.parse(window.regdata)
      var issuerFullName = ''
      var issuerShortName = ''
      var issuerINN = ''
      var issuerKPP = ''
      var issuerOGRN = ''
      var issuerLegalAddress = ''
      var errors = false

      if (regData !== null && regData.formdata !== null) {
        issuerFullName = regData.formdata.issuer_full_name
        issuerShortName = regData.formdata.issuer_short_name
        issuerINN = regData.formdata.issuer_inn
        issuerKPP = regData.formdata.issuer_kpp
        issuerOGRN = regData.formdata.issuer_ogrn
        issuerLegalAddress = regData.formdata.issuer_legal_address
        errors = regData.errors
      }

      return {
        product: 'BankGuaranteeProduct',
        party: issuerShortName,
        party_ogrn: issuerOGRN,
        party_inn: issuerINN,
        party_kpp: issuerKPP,
        party_full_name: issuerFullName,
        party_short_name: issuerShortName,
        party_legal_address: issuerLegalAddress,
        comment: document.getElementById('app').getAttribute('comment'),

        errors: errors,
        org_add_data_visible: false,

        action: ''
      }
    },
    watch: {
      product (e) {
        window.location.hash = '/' + this.product
      }
    },
    created () {
      window.location.hash = '/' + this.product
    },
    mounted () {
      var vue = this
      jQuery('.party input').suggestions({
        serviceUrl: 'https://suggestions.dadata.ru/suggestions/api/4_1/rs',
        token: this.token,
        type: 'PARTY',
        count: 7,
        onSelect: function (suggestion) {
          vue.party_ogrn = suggestion.data.ogrn
          vue.party_inn = suggestion.data.inn
          vue.party_kpp = suggestion.data.kpp
          vue.party_full_name = suggestion.data.name.full_with_opf
          vue.party_short_name = suggestion.data.name.short_with_opf
          vue.party_legal_address = suggestion.data.address.value
        }
      })
    }
  }
</script>

<style scoped>
  label {
    text-align: left;
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .5s ease;
  }

  .fade-enter, .fade-leave-active {
    opacity: 0
  }
</style>
