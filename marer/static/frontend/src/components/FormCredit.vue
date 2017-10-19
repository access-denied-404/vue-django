<template>
  <div class="form-credit">

    <div class="panel panel-info">
      <div class="panel-heading">Данные об испрашиваемом кредитном продукте</div>
      <div class="panel-body">

        <div class="row">

          <div class="col-md-6">
            <label>Вид кредитного продукта</label>
            <checkbox :name="'credit_product_is_credit'" v-model="credit_product_is_credit" type="primary">Кредит</checkbox>
            <checkbox :name="'credit_product_is_credit_line'" v-model="credit_product_is_credit_line" type="primary">Кредитная линия</checkbox>
            <checkbox :name="'credit_product_is_overdraft'" v-model="credit_product_is_overdraft" type="primary">Овердрафт</checkbox>
          </div>

          <div class="col-md-6">

            <div class="row">
              <div class="col-md-8"><bs-input :name="'bg_sum'" v-model="bg_sum" label="Сумма продукта" :mask="currency"></bs-input></div>
              <div class="col-md-4"><bs3-select-field v-model="bg_currency" :name="'bg_currency'" :label="'Валюта'" :options="[{value: 'rur', text:'Рубль'},{value: 'usd', text:'Доллар'},{value: 'eur', text:'Евро'}]"></bs3-select-field></div>
            </div>

            <div class="row">
              <div class="col-md-6"><bs-input :name="'credit_product_interest_rate'" v-model="credit_product_interest_rate" label="Ставка (в % годовых)"></bs-input></div>
              <div class="col-md-6"><bs3-select-field v-model="credit_repayment_schedule" :name="'credit_repayment_schedule'" :label="'График погашения'" :options="[{value: 'equal_shares', text:'Равными долями'},{value: 'end_of_term', text:'В конце срока'}]"></bs3-select-field></div>
            </div>

          </div>
        </div>

        <div class="row">
          <div class="col-md-6"><bs-input :name="'credit_product_term'" v-model="credit_product_term" label="Срок кредитного продукта"></bs-input></div>
          <div class="col-md-6"><bs-input :name="'credit_product_cl_tranche_term'" v-model="credit_product_cl_tranche_term" label="Срок транша (в случае кредитной линии)"></bs-input></div>
        </div>


        <div class="row">
          <div class="col-md-12"><bs-input :name="'credit_purpose'" v-model="credit_purpose" label="Цель кредита (подробно)"></bs-input></div>
        </div>

        <div class="row">
          <div class="col-md-12"><bs-input :name="'credit_repayment_sources'" v-model="credit_repayment_sources" label="Источники погашения"></bs-input></div>
        </div>

      </div>
    </div>

  </div>
</template>

<script>
//  import jQuery from 'jquery'
  import moment from 'moment'
//  import _ from 'lodash'
  import {input, checkbox} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'

  moment.locale = 'ru'
//  let dateformat = 'DD.MM.YYYY'

  export default {
    name: 'form-credit',
    components: {
      'bs-input': input,
      'checkbox': checkbox,
      'bs3-select-field': BS3SelectField,
      'bs3-radio-field': BS3RadioField,
      'date-time-picker': DateTimePicker
    },
    data () {
      var regData = JSON.parse(window.regdata)

      if (regData !== null && regData.formdata !== null) {
        return {
          credit_product_is_credit: regData.formdata.credit_product_is_credit,
          credit_product_is_credit_line: regData.formdata.credit_product_is_credit_line,
          credit_product_is_overdraft: regData.formdata.credit_product_is_overdraft,
          credit_product_interest_rate: regData.formdata.credit_product_interest_rate,
          credit_repayment_schedule: regData.formdata.credit_repayment_schedule,
          credit_product_term: regData.formdata.credit_product_term,
          credit_product_cl_tranche_term: regData.formdata.credit_product_cl_tranche_term,
          credit_purpose: regData.formdata.credit_purpose,
          credit_repayment_sources: regData.formdata.credit_repayment_sources,

          bg_sum: regData.formdata.bg_sum,
          bg_currency: regData.formdata.bg_currency
        }
      } else {
        return {
          credit_product_is_credit: '',
          credit_product_is_credit_line: '',
          credit_product_is_overdraft: '',
          credit_product_interest_rate: '',
          credit_repayment_schedule: '',
          credit_product_term: '',
          credit_product_cl_tranche_term: '',
          credit_purpose: '',
          credit_repayment_sources: '',

          bg_sum: '',
          bg_currency: ''
        }
      }
    },
    methods: {
      bg_currency (value) {
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
