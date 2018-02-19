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
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Заключение управления документарных операций</div>
              <div class="panel-body">

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_all_bank_liabilities_less_than_max" :type="'primary'">
                      Лимит на Принципала (группу взаимосвязанных Заемщиков) ВСЕХ обязательств Банка менее 18 000 000 руб
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_executed_contracts_on_44_or_223_or_185_fz" :type="'primary'">
                      Клиент исполнил не менее 1 контракта в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ (615 ПП)
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_executed_goverment_contract_for_last_3_years" :type="'primary'">
                      Наличие исполненного государственного контракта за последние 3 года
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_contract_has_prepayment" :type="'primary'">
                      Контракт предусматривает выплату аванса
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_executed_contracts_with_comparable_advances" :type="'primary'">
                      Клиент исполнял контракты с авансами сопоставимого или большего размера (допустимое отклонение в меньшую сторону не более 50 % включительно)
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz" :type="'primary'">
                      Факт исполнения не менее 5 контрактов, заключенных в рамках законов № 44-ФЗ (включая № 94-ФЗ), 223-ФЗ, 185-ФЗ (615 ПП)
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs" :type="'primary'">
                      Выручка Клиента за последний завершенный год не менее, чем в 5 раз превышает сумму запрашиваемой и действующих в Банке гарантий
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_has_garantor_for_advance_related_requirements" :type="'primary'">
                      Наличие Поручителя юридического лица удовлетворяющим одному из предыдущих трех условий
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_contract_price_reduction_lower_than_50_pct_on_supply_contract" :type="'primary'">
                      Снижение цены Контракта менее 50% если предмет контракта «Поставка»
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets" :type="'primary'">
                      Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов Клиента
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets" :type="'primary'">
                      Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов Клиента
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_need_to_check_real_of_issuer_activity" :type="'primary'">
                      Есть необходимость оценки реальности деятельности
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_real_of_issuer_activity_confirms" :type="'primary'">
                      Реальность деятельности подтверждается
                    </checkbox>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_contract_corresponds_issuer_activity" :type="'primary'">
                      Контракт соответствует профилю деятельности клиента
                    </checkbox>
                  </div>
                </div>

                <!-- only big conclusion fields -->
                <div v-if="this.issue.bg_sum >= 1500000">
                  <div class="row">
                    <div class="col-md-12">
                      <checkbox :checked.sync="issue.contract_advance_requirements_fails" :type="'primary'">
                        Не выполняются требования к авансированию (при наличии в контракте аванса)
                      </checkbox>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-12">
                      <checkbox :checked.sync="issue.is_issuer_has_bad_credit_history" :type="'primary'">
                        Наличие текущей просроченной ссудной задолженности и отрицательной кредитной истории в кредитных организациях
                      </checkbox>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-12">
                      <checkbox :checked.sync="issue.is_issuer_has_blocked_bank_account" :type="'primary'">
                        Наличие информации о блокировке счетов
                      </checkbox>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4 col-md-push-4">
                    <label>
                      Объем обязательств банка
                    </label>
                    <input type="number" class="form-control pull-right" v-model="issue.total_bank_liabilities_vol"/>
                  </div>
                </div>

              </div>
            </div>
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
