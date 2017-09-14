<template>
  <div class="form-bank-guarantee">
    <fieldset>
      <legend>Сведения о тендере</legend>

      <bs-input
        :name="'gos_number'"
        v-model="gos_number"
        label="Госномер тендера"
        required
      ></bs-input>

      <bs3-radio-field
        :name="'law'"
        v-model="law"
        label="Закон исполнения торгов"
        :options="[
          {value: '44_fz', text:'44-ФЗ'},
          {value: '223_fz', text:'223-ФЗ'}
        ]"
      ></bs3-radio-field>

      <bs-input
        :name="'placement_type'"
        v-model="placement_type"
        label="Способ определения поставщика"
      ></bs-input>

      <div class="row">
        <div class="col-md-6">

          <div class="form-group">
            <label>Дата публикации</label>
            <date-time-picker
              v-model="publish_datetime"
              :config="{'sideBySide':true,'locale':'ru'}"
            ></date-time-picker>
          </div>

        </div>
        <div class="col-md-6">

          <bs-input
            :name="'start_cost'"
            v-model="start_cost"
            label="НМЦК — начальная максимальная цена контракта"
            :mask="currency"
          ></bs-input>

        </div>
      </div>

    </fieldset>

    <fieldset>
      <legend>Сведения об организаторе тендера</legend>

      <bs-input
        :name="'publisher.full_name'"
        v-model="publisher.full_name"
        label="Наименование — полное наименование организации"
      ></bs-input>

      <bs-input
        :name="'publisher.legal_address'"
        v-model="publisher.legal_address"
        label="Адрес — юридический адрес организации"
      ></bs-input>

      <div class="row">
        <div class="col-md-4">

          <bs-input
            :name="'publisher.inn'"
            v-model="publisher.inn"
            label="ИНН"
          ></bs-input>

        </div>
        <div class="col-md-4">

          <bs-input
            :name="'publisher.kpp'"
            v-model="publisher.kpp"
            label="КПП"
          ></bs-input>

        </div>
        <div class="col-md-4">

          <bs-input
            :name="'publisher.ogrn'"
            v-model="publisher.ogrn"
            label="ОГРН"
          ></bs-input>

        </div>
      </div>

    </fieldset>

    <fieldset>
      <legend>Сведение об истребуемой гарантии</legend>

      <bs3-radio-field
        :name="'ensure_type'"
        v-model="ensure_type"
        label="Тип БГ"
        :options="[
          {value: 'contract', text:'Обеспечение исполнения контракта'},
          {value:'application', text:'Обеспечение заявки'}
        ]"
      ></bs3-radio-field>

      <div class="row">
        <div class="col-md-6">

          <bs-input
            :name="'ensure_cost'"
            v-model="ensure_cost"
            label="Требуемая сумма БГ"
            :mask="currency"
          ></bs-input>

        </div>
        <div class="col-md-6">

          <bs3-select-field
            v-model="currency_code"
            :name="'currency_code'"
            :label="'Валюта'"
            :options="[
          {value: 'rur', text:'Рубль'},
          {value: 'usd', text:'Доллар'},
          {value: 'eur', text:'Евро'},
        ]"
          ></bs3-select-field>

        </div>
      </div>

      <checkbox v-model="prepaid" true-value="1" type="success">Наличие аванса</checkbox>

      <bs3-radio-field
        :name="'contract_type'"
        v-model="contract_type"
        label="Тип контракта"
        :options="[
          {value: 'product', text:'поставка товара'},
          {value: 'service', text:'оказание услуг'},
          {value: 'work', text:'выполнение работ'}
        ]"
      ></bs3-radio-field>

      <div class="row">
        <div class="col-md-4">

          <div class="form-group">
            <label>Сроки БГ с</label>
            <date-time-picker
              v-model="date_from"
              :config="{'sideBySide':true,'locale':'ru'}"
            ></date-time-picker>
          </div>

        </div>
        <div class="col-md-4">

          <div class="form-group">
            <label>Сроки БГ по</label>
            <date-time-picker
              v-model="date_to"
              :config="{'sideBySide':true,'locale':'ru'}"
            ></date-time-picker>
          </div>

        </div>
        <div class="col-md-4">

          <bs-input
            :name="'date_range'"
            v-model="date_range"
            label="Срок БГ, дней"
            readonly
          ></bs-input>

        </div>
      </div>

      <bs-input
        :name="'deadline'"
        v-model="deadline"
        label="Крайний срок выдачи"
      ></bs-input>
    </fieldset>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  import _ from 'lodash'
  import {input, checkbox} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'

  export default {
    name: 'form-bank-guarantee',
    components: {
      'bs-input': input,
      'checkbox': checkbox,
      'bs3-select-field': BS3SelectField,
      'bs3-radio-field': BS3RadioField,
      'date-time-picker': DateTimePicker
    },
    data () {
      return {
        gos_number: '',
        law: '',
        placement_type: '',
        publish_datetime: '',
        start_cost: '',
        publisher: {
          full_name: '',
          legal_address: '',
          inn: '',
          kpp: '',
          ogrn: ''
        },
        ensure_type: '',
        application_ensure_cost: '',
        contract_execution_ensure_cost: '',
        currency_code: '',
        prepaid: '',
        contract_type: '',
        date_from: '',
        date_to: '',
        deadline: ''
      }
    },
    computed: {
      ensure_cost: {
        get () {
          if (this.ensure_type === 'contract') {
            return this.contract_execution_ensure_cost
          }
          if (this.ensure_type === 'application') {
            return this.application_ensure_cost
          }
          return ''
        },
        set () {
        }
      },
      date_range: {
        get () {
          if (this.date_from && this.date_to) {
            return Math.ceil((this.date_to - this.date_from) / 3600 / 24 / 1000)
          }
          return ''
        },
        set () {
        }
      }
    },
    watch: {
      gos_number: _.debounce(function () {
        jQuery.getJSON('/rest/tender?format=json&gos_number=' + this.gos_number, (data, status, xhr) => {
          this.law = data.law
          this.placement_type = data.placement_type
          this.publish_datetime = data.publish_datetime
          this.start_cost = data.start_cost
          this.publisher.full_name = data.publisher.full_name
          this.publisher.legal_address = data.publisher.legal_address
          this.publisher.inn = data.publisher.inn
          this.publisher.kpp = data.publisher.kpp
          this.publisher.ogrn = data.publisher.ogrn
          this.application_ensure_cost = data.application_ensure_cost
          this.contract_execution_ensure_cost = data.contract_execution_ensure_cost
          this.currency_code = data.currency_code
        })
      }, 1000)
    },
    methods: {
      currency (value) {
        return value
          .trim()
          .slice(
            0,
            value.indexOf('.') === -1
              ? value.length
              : value.indexOf('.') + 3
          )
          .replace(/[^\d.]+/, '')
      }
    }
  }
</script>

<style scoped>
  fieldset {
    border: 1px groove #ddd !important;
    padding: 0 1.4em 1.4em 1.4em !important;
    margin: 0 0 1.5em 0 !important;
    -webkit-box-shadow: 0px 0px 0px 0px #000;
    box-shadow: 0px 0px 0px 0px #000;
  }

  legend {
    font-size: 1.2em !important;
    font-weight: bold !important;
    text-align: left !important;
    width: auto;
    padding: 0 10px;
    border-bottom: none;
  }
</style>
