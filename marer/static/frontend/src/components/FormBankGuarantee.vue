<template>
  <div class="form-bank-guarantee">

    <input type="hidden" name="bg_currency" :value="bg_currency">
    <input type="hidden" name="bg_start_date" :value="bg_start_date">

    <input type="hidden" name="tender_exec_law" :value="tender_exec_law">
    <input type="hidden" name="tender_placement_type" :value="tender_placement_type">
    <input type="hidden" name="tender_publish_date" :value="tender_publish_date">
    <input type="hidden" name="tender_start_cost" :value="tender_start_cost">

    <input type="hidden" name="tender_responsible_full_name" :value="tender_responsible_full_name">
    <input type="hidden" name="tender_responsible_legal_address" :value="tender_responsible_legal_address">
    <input type="hidden" name="tender_responsible_inn" :value="tender_responsible_inn">
    <input type="hidden" name="tender_responsible_kpp" :value="tender_responsible_kpp">
    <input type="hidden" name="tender_responsible_ogrn" :value="tender_responsible_ogrn">
    <input type="hidden" name="tender_contract_subject" :value="tender_contract_subject"></input>

    <div class="panel panel-info">
      <div class="panel-heading">Сведения о тендере</div>
      <div class="panel-body">

        <div class="row">
          <div class="col-md-12"><bs-input :name="'tender_gos_number'" v-model="tender_gos_number" label="Госномер тендера или ссылка на закупку" required></bs-input></div>
        </div>

        <fieldset>
          <legend>
            <a class="btn btn-link btn-xs" v-on:click="tender_add_data_visible = !tender_add_data_visible">
              <span class="glyphicon glyphicon-triangle-bottom" v-if="tender_add_data_visible"></span>
              <span class="glyphicon glyphicon-triangle-right" v-else="tender_add_data_visible"></span>
              Подробности
            </a>
          </legend>

          <div class="row" v-if="tender_add_data_visible">
            <div class="col-md-6">
              <bs3-radio-field
                :name="'tender_exec_law'"
                v-model="tender_exec_law"
                label="Закон исполнения торгов"
                :options="[
                  {value: '44-fz', text:'44-ФЗ'},
                  {value: '223-fz', text:'223-ФЗ'},
                  {value: '185-fz', text:'185-ФЗ'}
                ]"
                :cols="3"
              ></bs3-radio-field>
            </div>
          </div>

          <div class="row" v-if="tender_add_data_visible">

            <div class="col-md-5"><div class="form-group"><bs-input :name="'tender_placement_type'" v-model="tender_placement_type" label="Способ определения поставщика"></bs-input></div></div>
            <div class="col-md-3"><label>Дата публикации</label><date-time-picker :name="'tender_publish_date'" v-model="tender_publish_date" :config="{'format':'L','locale':'ru'}"></date-time-picker></div>
            <div class="col-md-4"><bs-input :name="'tender_start_cost'" v-model="tender_start_cost" label="Начальная цена контракта" :mask="currency"></bs-input></div>
          </div>


          <fieldset v-if="tender_add_data_visible">
            <legend>Организатор закупки</legend>


            <div class="row">
              <div class="col-md-12"><bs-input :name="'tender_responsible_full_name'" v-model="tender_responsible_full_name" label="Полное наименование организации"></bs-input></div>
            </div>
            <div class="row">
              <div class="col-md-12"><bs-input :name="'tender_responsible_legal_address'" v-model="tender_responsible_legal_address" label="Юридический адрес"></bs-input></div>
            </div>
            <div class="row">
              <div class="col-md-4"><bs-input :name="'tender_responsible_inn'" v-model="tender_responsible_inn" label="ИНН"></bs-input></div>
              <div class="col-md-4"><bs-input :name="'tender_responsible_kpp'" v-model="tender_responsible_kpp" label="КПП"></bs-input></div>
              <div class="col-md-4"><bs-input :name="'tender_responsible_ogrn'" v-model="tender_responsible_ogrn" label="ОГРН"></bs-input></div>
            </div>

          </fieldset>

        </fieldset>

      </div>
    </div>

    <div class="panel panel-info">
      <div class="panel-heading">Сведения об истребуемой гарантии</div>
      <div class="panel-body">
        <div class="row">

          <div class="col-md-8">

            <div class="row">
              <div class="col-md-4">
                <bs-input
                  :name="'bg_sum'"
                  v-model="bg_sum"
                  label="Требуемая сумма"
                  :mask="currency"
                  v-bind:class="{'has-error': !sum_is_appropriate}"
                ></bs-input>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <label>Сроки БГ, по</label>
                  <date-time-picker
                    :name="'bg_end_date'"
                    v-model="bg_end_date"
                    :config="{'format':'L','locale':'ru'}"
                    required
                  ></date-time-picker>
                </div>
              </div>
              <div class="col-md-4">
                <bs-input
                  :name="'date_range'"
                  v-model="date_range"
                  label="Срок БГ, месяцев"
                  readonly
                  required
                  v-bind:class="{'has-error': !date_range_is_appropriate}"
                ></bs-input>
              </div>
            </div>

          </div>

          <div class="col-md-4">
            <bs3-radio-field :name="'bg_type'" v-model="bg_type" label="Тип БГ" :options="[{value: 'contract_execution', text:'Исполнение контракта'}, {value:'application_ensure', text:'Обеспечение заявки'}]"></bs3-radio-field>
            <checkbox :name="'tender_has_prepayment'" v-model="tender_has_prepayment" type="primary">Наличие аванса</checkbox>
          </div>

        </div>

      </div>
    </div>

    <div class="panel panel-info">
    <div class="panel-heading" data-toggle="collapse" data-target="#panel1">Бухгалтерская отчетность</div>
    <div class="panel-body collapse in" id="panel1">
        <div class="container-fluid">

            <div class="row">
                <div class="col-md-4 h4">Наименование показателя</div>
                <div class="col-md-8">
                    <div class="col-md-4 h5">Код строки</div>
                    <div class="col-md-4 h6">За последний отчётный период (2016 г.)</div>
                    <div class="col-md-4 h6">Результат за последний квартал (2017 г.)</div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">Чистые активы</div>
                <div class="col-md-8">
                    <div class="col-md-4">1300</div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_1300_offset_1" v-model="balance_code_1300_offset_1" />
                    </div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_1300_offset_0" v-model="balance_code_1300_offset_0" />
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">Валюта баланса</div>
                <div class="col-md-8">
                    <div class="col-md-4">1600</div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_1600_offset_1" v-model="balance_code_1600_offset_1" />
                    </div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_1600_offset_0" v-model="balance_code_1600_offset_0" />
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">Выручка</div>
                <div class="col-md-8">
                    <div class="col-md-4">2110</div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_2110_offset_1" v-model="balance_code_2110_offset_1" />
                    </div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_2110_offset_0" v-model="balance_code_2110_offset_0" />
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">Прибыль</div>
                <div class="col-md-8">
                    <div class="col-md-4">2400</div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_2400_offset_1" v-model="balance_code_2400_offset_1" />
                    </div>
                    <div class="col-md-4">
                      <input class="form-control input-sm" name="balance_code_2400_offset_0" v-model="balance_code_2400_offset_0" />
                    </div>
                </div>
            </div>

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
          tender_contract_subject: regData.formdata.tender_contract_subject,

          tender_responsible_full_name: regData.formdata.tender_responsible_full_name,
          tender_responsible_legal_address: regData.formdata.tender_responsible_legal_address,
          tender_responsible_inn: regData.formdata.tender_responsible_inn,
          tender_responsible_kpp: regData.formdata.tender_responsible_kpp,
          tender_responsible_ogrn: regData.formdata.tender_responsible_ogrn,

          balance_code_1300_offset_1: regData.formdata.balance_code_1300_offset_1,
          balance_code_1300_offset_0: regData.formdata.balance_code_1300_offset_0,
          balance_code_1600_offset_1: regData.formdata.balance_code_1600_offset_1,
          balance_code_1600_offset_0: regData.formdata.balance_code_1600_offset_0,
          balance_code_2110_offset_1: regData.formdata.balance_code_2110_offset_1,
          balance_code_2110_offset_0: regData.formdata.balance_code_2110_offset_0,
          balance_code_2400_offset_1: regData.formdata.balance_code_2400_offset_1,
          balance_code_2400_offset_0: regData.formdata.balance_code_2400_offset_0,

          bg_sum: regData.formdata.bg_sum,
          bg_type: regData.formdata.bg_type,
          bg_currency: 'rur',
          bg_start_date: regData.formdata.bg_start_date,
          bg_end_date: moment(regData.formdata.bg_end_date, dateformat),

          bg_commercial_contract_subject: regData.formdata.bg_commercial_contract_subject,
          bg_commercial_contract_place_of_work: regData.formdata.bg_commercial_contract_place_of_work,
          bg_commercial_contract_sum: regData.formdata.bg_commercial_contract_sum,
          bg_commercial_contract_sign_date: moment(regData.formdata.bg_commercial_contract_sign_date, dateformat),
          bg_commercial_contract_end_date: moment(regData.formdata.bg_commercial_contract_end_date, dateformat),

          is_tender_info_panel_visible: true,
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

          tender_collect_start_date: '',
          tender_collect_end_date: '',
          tender_finish_date: '',

          tender_has_prepayment: '',
          tender_contract_type: '',
          tender_contract_subject: '',

          tender_responsible_full_name: '',
          tender_responsible_legal_address: '',
          tender_responsible_inn: '',
          tender_responsible_kpp: '',
          tender_responsible_ogrn: '',

          bg_sum: '',
          bg_type: 'contract_execution',
          bg_currency: 'rur',
          bg_start_date: moment().format(dateformat),
          bg_end_date: '',

          bg_commercial_contract_subject: '',
          bg_commercial_contract_place_of_work: '',
          bg_commercial_contract_sum: '',
          bg_commercial_contract_sign_date: '',
          bg_commercial_contract_end_date: '',

          balance_code_1300_offset_1: '0',
          balance_code_1300_offset_0: '0',
          balance_code_1600_offset_1: '0',
          balance_code_1600_offset_0: '0',
          balance_code_2110_offset_1: '0',
          balance_code_2110_offset_0: '0',
          balance_code_2400_offset_1: '0',
          balance_code_2400_offset_0: '0',
          is_tender_info_panel_visible: true,
          tender_add_data_visible: false
        }
      }
    },
    computed: {
      date_range: {
        get () {
          if (this.bg_end_date) {
            let val
            let start = moment(this.bg_start_date, dateformat)
            let end = this.bg_end_date
            val = 1 + (end.year() - start.year()) * 12 + end.month() - start.month()
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
      },
      date_range_is_appropriate: {
        get () {
          return this.date_range > 0 && this.date_range <= 30
        }
      },
      sum_is_appropriate: {
        get () {
          return this.bg_sum > 0 && this.bg_sum <= 18000000
        }
      }
    },
    watch: {
      tender_gos_number: _.debounce(function () {
        jQuery.getJSON('/rest/tender?format=json&gos_number=' + this.tender_gos_number, (data, status, xhr) => {
          this.tender_exec_law = data.law
          this.tender_placement_type = data.placement_type
          this.tender_publish_date = data.publish_date
          this.tender_collect_start_date = data.collect_start_date
          this.tender_collect_end_date = data.collect_end_date
          this.tender_finish_date = data.finish_date
          this.tender_start_cost = data.start_cost
          this.tender_responsible_full_name = data.publisher.full_name
          this.tender_responsible_legal_address = data.publisher.legal_address
          this.tender_responsible_inn = data.publisher.inn
          this.tender_responsible_kpp = data.publisher.kpp
          this.tender_responsible_ogrn = data.publisher.ogrn
          this.tender_application_ensure_cost = data.application_ensure_cost
          this.tender_contract_execution_ensure_cost = data.contract_execution_ensure_cost
          this.tender_contract_subject = data.description
          this.process_bg_type()
        })
      }, 1000),
      tender_exec_law: _.debounce(function () {
        this.is_tender_info_panel_visible = this.get_if_tender_info_panel_visible()
      }, 200),
      bg_type: _.debounce(function () {
        this.process_bg_type()
      }, 200)
    },
    mounted () {
      this.is_tender_info_panel_visible = this.get_if_tender_info_panel_visible()
    },
    methods: {
      get_if_tender_info_panel_visible () {
        return this.tender_exec_law === '44-fz' ||
          this.tender_exec_law === '223-fz' ||
          this.tender_exec_law === '185-fz'
      },
      process_bg_type () {
        if (this.bg_type === 'application_ensure') {
          if (!this.bg_sum || this.bg_sum === '' || this.bg_sum === this.tender_contract_execution_ensure_cost) this.bg_sum = this.tender_application_ensure_cost

          if (this.tender_collect_end_date && this.tender_collect_end_date !== '') {
            this.bg_end_date = moment(this.tender_collect_end_date, dateformat).add(90, 'days')
          }
        }
        if (this.bg_type === 'contract_execution') {
          if (!this.bg_sum || this.bg_sum === '' || this.bg_sum === this.tender_application_ensure_cost) if (this.tender_contract_execution_ensure_cost) this.bg_sum = this.tender_contract_execution_ensure_cost
        }
      }
    }
  }
</script>
