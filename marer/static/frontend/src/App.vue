<template>
  <div id="app-root">
    <form method="post" :action="this.getFormAction()">

      <div class="alert alert-danger" v-if="errors.stop_factors">
        <p v-for="err in errors.stop_factors" class="text-center">
          <span class="h2">{{ err }}</span>
        </p>
      </div>

      <div class="alert alert-danger" v-if="errors.already_has_an_agent">
        <p v-for="err in errors.already_has_an_agent" class="text-center">
          <span class="h2">{{ err }}</span>
        </p>
      </div>

      <div class="alert alert-danger" v-if="errors.__all__">
        <ul>
          <li v-for="err in errors.__all__">{{ err }}</li>
        </ul>
      </div>

      <div class="panel panel-info">
        <div class="panel-heading">Оформление заявки</div>
        <div class="panel-body">
          <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">
          <input type="hidden" name="product" :value="product">

          <input type="hidden" name="issuer_ogrn" :value="party_ogrn">
          <input type="hidden" name="issuer_inn" :value="party_inn">
          <input type="hidden" name="issuer_kpp" :value="party_kpp">
          <input type="hidden" name="issuer_full_name" :value="party_full_name">
          <input type="hidden" name="issuer_short_name" :value="party_short_name">
          <input type="hidden" name="issuer_legal_address" :value="party_legal_address">

          <div class="row">
            <div class="col-md-12">
              <bs-input
                :placeholder="'Название, ИНН, ОГРН или адрес организации'"
                :name="'party'"
                class="party"
                :label="'Организация-заявитель'"
                v-model="party"
              ></bs-input>
            </div>
          </div>

          <fieldset>
            <legend>
              <a class="btn btn-link btn-xs" v-on:click="org_add_data_visible = !org_add_data_visible">
                <span class="glyphicon glyphicon-triangle-bottom" v-if="org_add_data_visible"></span>
                <span class="glyphicon glyphicon-triangle-right" v-else="org_add_data_visible"></span>
                Подробности
              </a>
            </legend>

            <div class="row" v-if="org_add_data_visible">
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

            <div class="row" v-if="org_add_data_visible">
              <div class="col-md-12">
                <bs-input
                  :name="'issuer_legal_address'"
                  :label="'Юридический адрес'"
                  v-model="party_legal_address"
                ></bs-input>
              </div>
            </div>

            <div class="row" v-if="org_add_data_visible">
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
          </fieldset>

        </div>
      </div>
      <transition appear name="fade" mode="out-in">
        <router-view></router-view>
      </transition>
      <div class="text-center">
        <button type="submit" v-on:click="action = 'save'" class="btn btn-primary spinjs">Сохранить черновик</button>
        &nbsp;
        <button type="submit" v-on:click="action = 'next'" class="btn btn-success spinjs">Далее</button>

        <input type="hidden" name="action" :value="action"/>
      </div>
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
    props: ['csrf', 'products', 'token', 'issue_id'],
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
    methods: {
      getFormAction: function () {
        if (this.issue_id) {
          return '/cabinet/requests/' + this.issue_id + '/reg'
        } else {
          return ''
        }
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
