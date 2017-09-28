<template>
  <div id="app-root">
    <form method="post">
      <div class="panel panel-primary">
        <div class="panel-heading">Оформление заявки</div>
        <div class="panel-body">
          <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">

          <div class="row">
            <div class="col-md-6">
              <bs3-select-field
                v-model="product"
                :name="'product'"
                :label="'Тип заявки'"
                :options="products"
              ></bs3-select-field>
            </div>
            <div class="col-md-6">
              <bs-input
                :name="'party'"
                class="party"
                :label="'Организация'"
                v-model="party"
              ></bs-input>
            </div>
          </div>

          <div class="row">
            <div class="col-md-8">
              <bs-input
                :name="'issuer_full_name'"
                :label="'Полное наименование'"
                v-model="party_full_name"
              ></bs-input>
            </div>
            <div class="col-md-4">
              <bs-input
                :name="'issuer_short_name'"
                :label="'Краткое наименование'"
                v-model="party_short_name"
              ></bs-input>
            </div>
          </div>

          <div class="row">
            <div class="col-md-12">
              <bs-input
                :name="'issuer_legal_address'"
                :label="'Юридический адрес'"
                v-model="party_legal_address"
              ></bs-input>
            </div>
          </div>

          <div class="row">
            <div class="col-md-4">
              <bs-input
                :name="'issuer_ogrn'"
                :label="'ОГРН'"
                v-model="party_ogrn"
              ></bs-input></div>
            <div class="col-md-4">
              <bs-input
                :name="'issuer_inn'"
                :label="'ИНН'"
                v-model="party_inn"
              ></bs-input>
            </div>
            <div class="col-md-4">
              <bs-input
                :name="'issuer_kpp'"
                :label="'КПП'"
                v-model="party_kpp"
              ></bs-input>
            </div>
          </div>

        </div>
      </div>
      <transition appear name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
      <button type="submit" class="btn btn-primary center-block">Сохранить</button>
    </form>
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

      if (regData !== null && regData.formdata !== null) {
        issuerFullName = regData.formdata.issuer_full_name
        issuerShortName = regData.formdata.issuer_short_name
        issuerINN = regData.formdata.issuer_inn
        issuerKPP = regData.formdata.issuer_kpp
        issuerOGRN = regData.formdata.issuer_ogrn
        issuerLegalAddress = regData.formdata.issuer_legal_address
      }

      return {
        product: document.getElementById('app').getAttribute('product'),
        party: issuerShortName,
        party_ogrn: issuerOGRN,
        party_inn: issuerINN,
        party_kpp: issuerKPP,
        party_full_name: issuerFullName,
        party_short_name: issuerShortName,
        party_legal_address: issuerLegalAddress
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
