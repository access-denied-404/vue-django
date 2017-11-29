<template>
  <div class="form-bank-guarantee">

    <input type="hidden" name="tender_exec_law" :value="tender_exec_law">
    <input type="hidden" name="tender_placement_type" :value="tender_placement_type">
    <input type="hidden" name="tender_publish_date" :value="tender_publish_date">
    <input type="hidden" name="tender_start_cost" :value="tender_start_cost">

    <input type="hidden" name="tender_responsible_full_name" :value="tender_responsible_full_name">
    <input type="hidden" name="tender_responsible_legal_address" :value="tender_responsible_legal_address">
    <input type="hidden" name="tender_responsible_inn" :value="tender_responsible_inn">
    <input type="hidden" name="tender_responsible_kpp" :value="tender_responsible_kpp">
    <input type="hidden" name="tender_responsible_ogrn" :value="tender_responsible_ogrn">

    <div class="panel panel-info">
      <div class="panel-heading">Вид банковской гарантии</div>
      <div class="panel-body">

    <div class="row">
      <div class="col-md-12 text-center1">
        <bs3-radio-field
          :name="'tender_exec_law'"
          v-model="tender_exec_law"
          label=""
          :options="[
            {value: '44-fz', text:'44-ФЗ'},
            {value: '185-fz', text:'185-ФЗ'},
            {value: '223-fz', text:'223-ФЗ'}
          ]"
          :cols="4"
        ></bs3-radio-field>
        <!--<br/>-->
      </div>
    </div>

      </div>
    </div>

    <div class="panel panel-info" v-if="is_tender_info_panel_visible">
      <div class="panel-heading">Сведения о тендере</div>
      <div class="panel-body">
        <div class="row">
          <div class="col-md-12"><bs-input :name="'tender_gos_number'" v-model="tender_gos_number" label="Госномер тендера или ссылка на закупку" required></bs-input></div>
        </div>
        <div class="row">
          <div class="col-md-12 text-center">
            <a class="btn btn-link" v-on:click="tender_add_data_visible = !tender_add_data_visible">{{tender_add_data_switch_caption}}</a>
          </div>
        </div>
        <div class="row" v-if="tender_add_data_visible">
          <div class="col-md-5"><div class="form-group"><bs-input :name="'tender_placement_type'" v-model="tender_placement_type" label="Способ определения поставщика"></bs-input></div></div>
          <div class="col-md-3"><label>Дата публикации</label><date-time-picker :name="'tender_publish_date'" v-model="tender_publish_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div>
          <div class="col-md-4"><bs-input :name="'tender_start_cost'" v-model="tender_start_cost" label="Начальная цена контракта" :mask="currency"></bs-input></div>
        </div>
      </div>
    </div>

    <div class="panel panel-info" v-if="is_contract_info_panel_visible">
      <div class="panel-heading">Сведения о контракте</div>
      <div class="panel-body">

        <div class="row">
          <div class="col-md-12"><bs-input :name="'bg_commercial_contract_subject'" v-model="bg_commercial_contract_subject" label="Предмет контракта"></bs-input></div>
        </div>
        <div class="row">
          <div class="col-md-12"><bs-input :name="'bg_commercial_contract_place_of_work'" v-model="bg_commercial_contract_place_of_work" label="Место выполнения работ"></bs-input></div>
        </div>
        <div class="row">
          <div class="col-md-4"><bs-input :name="'bg_commercial_contract_sum'" v-model="bg_commercial_contract_sum" label="Сумма контракта"></bs-input></div>
          <div class="col-md-4"><label>Дата заключения договора</label><date-time-picker :name="'bg_commercial_contract_sign_date'" v-model="bg_commercial_contract_sign_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div>
          <div class="col-md-4"><label>Дата завершения договора</label><date-time-picker :name="'bg_commercial_contract_end_date'" v-model="bg_commercial_contract_end_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div>
        </div>

      </div>
    </div>

    <div class="panel panel-info">
      <div class="panel-heading">Сведения об истребуемой гарантии</div>
      <div class="panel-body">
        <div class="row">

          <div class="col-md-8">

            <div class="row">
              <div class="col-md-4"><bs-input :name="'bg_sum'" v-model="bg_sum" label="Требуемая сумма" :mask="currency"></bs-input></div>
              <div class="col-md-3"><bs3-select-field v-model="bg_currency" :name="'bg_currency'" :label="'Валюта'" :options="[{value: 'rur', text:'Рубль'},{value: 'usd', text:'Доллар'},{value: 'eur', text:'Евро'}]"></bs3-select-field></div>
              <div class="col-md-5"><label>Крайний срок выдачи</label><date-time-picker :name="'bg_deadline_date'" v-model="bg_deadline_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div>
            </div>

            <div class="row">
              <div class="col-md-4"><div class="form-group"><label>Сроки БГ с</label><date-time-picker :name="'bg_start_date'" v-model="bg_start_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div></div>
              <div class="col-md-4"><div class="form-group"><label>Сроки БГ по</label><date-time-picker :name="'bg_end_date'" v-model="bg_end_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div></div>
              <div class="col-md-4"><bs-input :name="'date_range'" v-model="date_range" label="Срок БГ, дней" readonly></bs-input></div>
            </div>

          </div>

          <div class="col-md-4">
            <bs3-radio-field v-if="is_tender_info_panel_visible" :name="'bg_type'" v-model="bg_type" label="Тип БГ" :options="[{value: 'contract_execution', text:'Исполнение контракта'}, {value:'application_ensure', text:'Обеспечение заявки'}]"></bs3-radio-field>
            <bs3-radio-field :name="'tender_contract_type'" v-model="tender_contract_type" label="Тип контракта" :options="[{value: 'supply', text:'поставка товара'},{value: 'service', text:'оказание услуг'},{value: 'works', text:'выполнение работ'}]"></bs3-radio-field>
            <checkbox :name="'tender_has_prepayment'" v-model="tender_has_prepayment" type="primary">Наличие аванса</checkbox>
          </div>

        </div>

      </div>
    </div>

    <div class="panel panel-info" v-if="tender_add_data_visible && (is_tender_info_panel_visible || is_contract_info_panel_visible)">
      <div class="panel-heading" v-if="is_tender_info_panel_visible">Сведения об организаторе тендера</div>
      <div class="panel-heading" v-if="is_contract_info_panel_visible">Сведения о заказчике</div>
      <div class="panel-body">
        <div class="row">
          <div class="col-md-12"><bs-input :name="'tender_responsible_full_name'" v-model="tender_responsible_full_name" label="Наименование — полное наименование организации"></bs-input></div>
        </div>
        <div class="row">
          <div class="col-md-12"><bs-input :name="'tender_responsible_legal_address'" v-model="tender_responsible_legal_address" label="Адрес — юридический адрес организации"></bs-input></div>
        </div>
        <div class="row">
          <div class="col-md-4"><bs-input :name="'tender_responsible_inn'" v-model="tender_responsible_inn" label="ИНН"></bs-input></div>
          <div class="col-md-4"><bs-input :name="'tender_responsible_kpp'" v-model="tender_responsible_kpp" label="КПП"></bs-input></div>
          <div class="col-md-4"><bs-input :name="'tender_responsible_ogrn'" v-model="tender_responsible_ogrn" label="ОГРН"></bs-input></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
  import jQuery from 'jquery'
  import moment from 'moment'
  import _ from 'lodash'
  import {input, checkbox} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'

  moment.locale = 'ru'
  let dateformat = 'DD.MM.YYYY'

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
      var regData = JSON.parse(window.regdata)

      if (regData !== null && regData.formdata !== null) {
        return {
          tender_gos_number: regData.formdata.tender_gos_number,
          tender_exec_law: regData.formdata.tender_exec_law,
          tender_placement_type: regData.formdata.tender_placement_type,
          tender_publish_date: regData.formdata.tender_publish_date,
          tender_start_cost: regData.formdata.tender_start_cost,

          tender_application_ensure_cost: regData.formdata.tender_application_ensure_cost,
          tender_contract_execution_ensure_cost: regData.formdata.tender_contract_execution_ensure_cost,

          tender_has_prepayment: regData.formdata.tender_has_prepayment,
          tender_contract_type: regData.formdata.tender_contract_type,

          tender_responsible_full_name: regData.formdata.tender_responsible_full_name,
          tender_responsible_legal_address: regData.formdata.tender_responsible_legal_address,
          tender_responsible_inn: regData.formdata.tender_responsible_inn,
          tender_responsible_kpp: regData.formdata.tender_responsible_kpp,
          tender_responsible_ogrn: regData.formdata.tender_responsible_ogrn,

          bg_sum: regData.formdata.bg_sum,
          bg_type: regData.formdata.bg_type,
          bg_currency: regData.formdata.bg_currency,
          bg_start_date: moment(regData.formdata.bg_start_date, dateformat),
          bg_end_date: moment(regData.formdata.bg_end_date, dateformat),
          bg_deadline_date: regData.formdata.bg_deadline_date,

          bg_commercial_contract_subject: regData.formdata.bg_commercial_contract_subject,
          bg_commercial_contract_place_of_work: regData.formdata.bg_commercial_contract_place_of_work,
          bg_commercial_contract_sum: regData.formdata.bg_commercial_contract_sum,
          bg_commercial_contract_sign_date: moment(regData.formdata.bg_commercial_contract_sign_date, dateformat),
          bg_commercial_contract_end_date: moment(regData.formdata.bg_commercial_contract_end_date, dateformat),

          is_tender_info_panel_visible: true,
          is_contract_info_panel_visible: false,
          tender_add_data_visible: false
        }
      } else {
        return {
          tender_gos_number: '',
          tender_exec_law: '',
          tender_placement_type: '',
          tender_publish_date: '',
          tender_start_cost: '',

          tender_application_ensure_cost: '',
          tender_contract_execution_ensure_cost: '',

          tender_has_prepayment: '',
          tender_contract_type: '',

          tender_responsible_full_name: '',
          tender_responsible_legal_address: '',
          tender_responsible_inn: '',
          tender_responsible_kpp: '',
          tender_responsible_ogrn: '',

          bg_sum: '',
          bg_type: '',
          bg_currency: '',
          bg_start_date: '',
          bg_end_date: '',
          bg_deadline_date: '',

          bg_commercial_contract_subject: '',
          bg_commercial_contract_place_of_work: '',
          bg_commercial_contract_sum: '',
          bg_commercial_contract_sign_date: '',
          bg_commercial_contract_end_date: '',

          is_tender_info_panel_visible: true,
          is_contract_info_panel_visible: false,
          tender_add_data_visible: false
        }
      }
    },
    computed: {
      date_range: {
        get () {
          if (this.bg_start_date && this.bg_end_date) {
            let val
            val = Math.ceil((this.bg_end_date - this.bg_start_date) / 3600 / 24 / 1000)
            if (isNaN(val)) {
              return ''
            } else {
              return val
            }
          }
          return ''
        },
        set () {
        }
      },
      tender_add_data_switch_caption: {
        get () {
          if (this.tender_add_data_visible) {
            return 'Скрыть'
          } else {
            return 'Подробнее'
          }
        },
        set () {}
      }
    },
    watch: {
      tender_gos_number: _.debounce(function () {
        jQuery.getJSON('/rest/tender?format=json&gos_number=' + this.tender_gos_number, (data, status, xhr) => {
          this.tender_exec_law = data.law
          this.tender_placement_type = data.placement_type
          this.tender_publish_date = data.publish_datetime
          this.tender_start_cost = data.start_cost
          this.tender_responsible_full_name = data.publisher.full_name
          this.tender_responsible_legal_address = data.publisher.legal_address
          this.tender_responsible_inn = data.publisher.inn
          this.tender_responsible_kpp = data.publisher.kpp
          this.tender_responsible_ogrn = data.publisher.ogrn
          this.tender_application_ensure_cost = data.application_ensure_cost
          this.tender_contract_execution_ensure_cost = data.contract_execution_ensure_cost
          this.bg_currency = data.currency_code
        })
      }, 1000),
      tender_exec_law: _.debounce(function () {
        this.is_tender_info_panel_visible = this.get_if_tender_info_panel_visible()
        this.is_contract_info_panel_visible = this.get_is_contract_info_panel_visible()
      }, 200),
      bg_type: _.debounce(function () {
        if (this.bg_type === 'application_ensure') {
          if (!this.bg_sum || this.bg_sum === '' || this.bg_sum === this.tender_contract_execution_ensure_cost) this.bg_sum = this.tender_application_ensure_cost
        }
        if (this.bg_type === 'contract_execution') {
          if (!this.bg_sum || this.bg_sum === '' || this.bg_sum === this.tender_application_ensure_cost) this.bg_sum = this.tender_contract_execution_ensure_cost
        }
      }, 200)
    },
    mounted () {
      this.is_tender_info_panel_visible = this.get_if_tender_info_panel_visible()
      this.is_contract_info_panel_visible = this.get_is_contract_info_panel_visible()
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
      },
      get_if_tender_info_panel_visible () {
        return this.tender_exec_law === '44-fz' ||
          this.tender_exec_law === '223-fz' ||
          this.tender_exec_law === '185-fz'
      },
      get_is_contract_info_panel_visible () {
        return this.tender_exec_law === 'commercial'
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
