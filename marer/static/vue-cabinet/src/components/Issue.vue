<template>
  <div class="container">
    <div class="row">
      <h1 class="text-center">Заявка №{{issue.id}}</h1>
      <!--<div class="h4 text-center"><b>Банковская гарантия</b>-->
      <!--на сумму <b>16 000,00 руб.</b>-->
      <!--</div>-->
    </div>
    <div class="row">
      <issue-menu :id="this.issue.id"></issue-menu>
      <div class="col-md-9">
        <div class="panel panel-info">
          <div class="panel-heading">Сведения об истребуемой гарантии</div>
          <div class="panel-body">
            <div class="row">
              <div class="col-md-4" v-bind:class="{'has-error': !sum_is_appropriate}">
                <div class="form-group">
                  <label for="id_bg_sum">Требуемая сумма (не более 18 млн.)</label>
                  <money type="text" id="id_bg_sum" name="bg_sum"
                         v-bind="money_format" v-model="issue.bg_sum" class="form-control input"></money>
                </div>
              </div>
              <div class="col-md-2">
                <div class="form-group">
                  <label>Дата выдачи</label>
                  <date-time-picker
                    :name="'bg_start_date'"
                    v-model="issue.bg_start_date"
                    :config="{'format':'L','locale':'ru'}"
                    required
                  ></date-time-picker>
                </div>
              </div>
              <div class="col-md-2">
                <div class="form-group">
                  <label>Дата окончания</label>
                  <date-time-picker
                    :name="'bg_end_date'"
                    v-model="issue.bg_end_date"
                    :config="{'format':'L','locale':'ru'}"
                    required
                  ></date-time-picker>
                </div>
              </div>
              <div class="col-md-4">
                <bs-input
                  :name="'date_range'"
                  v-model="date_range"
                  label="Срок БГ, месяцев (не более 30)"
                  readonly
                  required
                  v-bind:class="{'has-error': !date_range_is_appropriate}"
                ></bs-input>
              </div>
            </div>

            <div class="row">
              <div class="col-md-8">
                <bs3-radio-field :name="'bg_type'" v-model="issue.bg_type" label="Тип БГ" :options="[
            {value: 'contract_execution', text:'Исполнение обязательств по контракту'},
            {value:'application_ensure', text:'Для обеспечения заявки на участие в конкурсе (тендерная гарантия)'},
            {value: 'refund_of_advance', text:'Возврат аванса'},
            {value: 'warranty_ensure', text:'Обеспечение гарантийных обязательств'}]"></bs3-radio-field>
              </div>

              <div class="col-md-4">
                <checkbox :name="'bg_is_benefeciary_form'" v-model="issue.bg_is_benefeciary_form" type="primary">
                  БГ по форме Бенефециара
                </checkbox>
                <checkbox :name="'tender_has_prepayment'" v-model="issue.tender_has_prepayment" type="primary">
                  Наличие аванса
                </checkbox>
                <checkbox :name="'is_indisputable_charge_off'" v-model="issue.is_indisputable_charge_off" type="primary">
                  Бесспорное списание
                </checkbox>
              </div>
            </div>
          </div>
        </div>
        <div class="panel panel-info">
          <div class="panel-heading">Оформление заявки</div>
          <div class="panel-body">
            <fieldset>
              <div class="row">
                <div class="col-md-8">
                  <bs-input
                    :name="'issuer_full_name'"
                    :label="'Полное наименование'"
                    v-model="issue.issuer_full_name"
                  ></bs-input>
                </div>
                <div class="col-md-4">
                  <bs-input
                    :name="'issuer_short_name'"
                    :label="'Краткое наименование'"
                    v-model="issue.issuer_short_name"
                  ></bs-input>
                </div>
              </div>

              <div class="row">
                <div class="col-md-12">
                  <bs-input
                    :name="'issuer_legal_address'"
                    :label="'Юридический адрес'"
                    v-model="issue.issuer_legal_address"
                  ></bs-input>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12">
                  <bs-input
                    :name="'issuer_fact_address'"
                    :label="'Фактический адрес'"
                    v-model="issue.issuer_fact_address"
                  ></bs-input>
                </div>
              </div>

              <div class="row">
                <div class="col-md-3">
                  <bs-input
                    :name="'issuer_ogrn'"
                    :label="'ОГРН'"
                    v-model="issue.issuer_ogrn"
                  ></bs-input>
                </div>
                <div class="col-md-3">
                  <bs-input
                    :name="'issuer_inn'"
                    :label="'ИНН'"
                    v-model="issue.issuer_inn"
                  ></bs-input>
                </div>
                <div class="col-md-3">
                  <bs-input
                    :name="'issuer_kpp'"
                    :label="'КПП'"
                    v-model="issue.issuer_kpp"
                  ></bs-input>
                </div>
                <div class="col-md-3">
                  <bs-input
                    :name="'issuer_okpo'"
                    :label="'ОКПО'"
                    v-model="issue.issuer_okpo"
                  ></bs-input>
                </div>
              </div>
              <div class="row">
                <div class="col-md-3">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_registration_date'"
                      :label="'Дата регистрации компании'"
                      v-model="issue.issuer_registration_date"
                    ></bs-input>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_ifns_reg_date'"
                      :label="'Дата постановки на учет в ИФНС'"
                      v-model="issue.issuer_ifns_reg_date"
                    ></bs-input>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label>Наличие просроченной задолженности по всем кредитам за последние 180 дней</label>
                    <bs-select :value.sync="issue.issuer_has_overdue_debts_for_last_180_days" :options="[{value: false, label: 'Нет'}, {value: true, label: 'Да'}]"></bs-select>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-4">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_okopf'"
                      :label="'Форма собственности (код ОКОПФ)'"
                      v-model="issue.issuer_okopf"
                    ></bs-input>
                  </div>
                </div>
                <div class="col-md-4">
                  <label>Система налогообложения</label>
                  <bs-select
                    :value.sync="issue.tax_system"
                    :options="[
                      {value: 'tax_usn', label: 'УСН'},
                      {value: 'tax_envd', label: 'ЕНВД'},
                      {value: 'tax_osn', label: 'ОСН'},
                      {value: 'tax_eshd', label: 'ЕСХД'}
                    ]"></bs-select>
                </div>
                <div class="col-md-4">
                  <div class="form-group">
                    <bs-input
                      :name="'avg_employees_cnt_for_prev_year'"
                      :label="'Средняя численность работников за предшествующий календарный год'"
                      v-model="issue.avg_employees_cnt_for_prev_year"
                    ></bs-input>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_accountant_org_or_person'"
                      :label="'ФИО главного бухгалтера / наименование организации, осуществляющей ведение бухгалтерского учёта'"
                      v-model="issue.issuer_accountant_org_or_person"
                    ></bs-input>
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-7">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_post_address'"
                      :label="'Почтовый адрес (для отправки банковской гарантии)'"
                      v-model="issue.issuer_post_address"
                    ></bs-input>
                  </div>
                </div>
                <div class="col-md-5">
                  <div class="form-group">
                    <bs-input
                      :name="'issuer_web_site'"
                      :label="'Web-сайт'"
                      v-model="issue.issuer_web_site"
                    ></bs-input>
                  </div>
                </div>
              </div>
            </fieldset>

          </div>
        </div>
        <div class="panel panel-info">
          <div class="panel-heading">Сведения о закупке</div>
          <div class="panel-body">

            <div class="row">
              <div class="col-md-12">
                <bs-input :name="'tender_gos_number'" v-model="issue.tender_gos_number" label="Номер закупки или ссылка"
                          required></bs-input>
              </div>
              <div class="col-md-6">
                <bs3-radio-field :name="'tender_exec_law'" v-model="issue.tender_exec_law"
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

            <fieldset>
              <div class="row" >

                <div class="col-md-5">
                  <div class="form-group">
                    <bs-input :name="'tender_placement_type'" v-model="issue.tender_placement_type" label="Способ определения поставщика"></bs-input>
                  </div>
                </div>
                <div class="col-md-3"><label>Дата публикации</label>
                  <date-time-picker :name="'tender_publish_date'" v-model="issue.tender_publish_date" :config="{'format':'L','locale':'ru'}"></date-time-picker>
                </div>
                <div class="col-md-4">
                  <label>Начальная цена контракта</label>
                  <money type="text" name="tender_start_cost" class="form-control input" v-model="issue.tender_start_cost" v-bind="money_format"></money>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12">
                  <bs-input :name="'tender_contract_subject'" v-model="issue.tender_contract_subject"
                            label="Предмет контракта"></bs-input>
                </div>
              </div>


              <fieldset>
                <legend>Бенефициар закупки</legend>


                <div class="row">
                  <div class="col-md-12">
                    <bs-input :name="'tender_responsible_full_name'" v-model="issue.tender_responsible_full_name" label="Полное наименование организации"></bs-input>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-12">
                    <bs-input :name="'tender_responsible_legal_address'" v-model="issue.tender_responsible_legal_address" label="Юридический адрес"></bs-input>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-4">
                    <bs-input :name="'tender_responsible_inn'" v-model="issue.tender_responsible_inn" label="ИНН"></bs-input>
                  </div>
                  <div class="col-md-4">
                    <bs-input :name="'tender_responsible_kpp'" v-model="issue.tender_responsible_kpp" label="КПП"></bs-input>
                  </div>
                  <div class="col-md-4">
                    <bs-input :name="'tender_responsible_ogrn'" v-model="issue.tender_responsible_ogrn" label="ОГРН"></bs-input>
                  </div>
                </div>
              </fieldset>

            </fieldset>

          </div>
        </div>

        <div class="row">
          <div class="col-md-12 text-center">
            <button class="btn btn-primary" type="button" v-on:click="save_issue">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
    <br/>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  import moment from 'moment'
  import {input, checkbox, select} from 'vue-strap'
  import DateTimePicker from 'vue-bootstrap-datetimepicker'
  import BS3SelectField from '@/components/inputs/BS3SelectField'
  import BS3RadioField from '@/components/inputs/BS3RadioField'
  import IssueMenu from '@/components/IssueMenu'
  import 'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css'
  import {Money} from 'v-money'

  moment.locale = 'ru'
  let dateformat = 'DD.MM.YYYY'

  export default {
    name: 'issue',
    components: {
      'bs-select': select,
      'bs-input': input,
      'checkbox': checkbox,
      'bs3-select-field': BS3SelectField,
      'bs3-radio-field': BS3RadioField,
      'date-time-picker': DateTimePicker,
      'Money': Money,
      'issue-menu': IssueMenu
    },
    props: ['id'],
    data () {
      return {
        api_url: window.debug ? 'http://localhost:8000/rest/issue/' : '/rest/issue/',
        issue: {}
      }
    },
    mounted: function () {
      jQuery.getJSON(this.api_url + this.$route.params.id + '?format=json', (data, status, xhr) => {
        this.update_form_data(data)
      })
    },
    computed: {
      date_range: {
        get () {
          if (this.issue.bg_end_date) {
            let val
            let start = moment(this.issue.bg_start_date, dateformat)
            let end = this.issue.bg_end_date
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
      }
    },
    methods: {
      update_form_data (data) {
        data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
        this.issue = data
        this.issue.bg_start_date = moment(data.bg_start_date, dateformat)
        this.issue.bg_end_date = moment(data.bg_end_date, dateformat)
        this.issue.bg_commercial_contract_sign_date = moment(data.bg_commercial_contract_sign_date, dateformat)
        this.issue.bg_commercial_contract_end_date = moment(data.bg_commercial_contract_end_date, dateformat)

        this.finance_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 2
        })
        this.legal_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 1
        })
        this.other_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 3
        })
      },
      save_issue () {
        jQuery.ajax(this.api_url + this.$route.params.id, this.issue, (data) => {
          this.update_form_data(data)
        })
      }
    }
  }
</script>
