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
        <div class="well well-sm dang text-center">
          <strong>
          Ссылка для клиента для заполнения анкеты и её подписания:
          </strong>
          http://sgbmarertest.ru/cabinet/requests/{{issue.id}}/rsr
          <a class="btn btn-link btn-xs" :href="'http://sgbmarertest.ru/cabinet/requests/' + issue.id + '/rsr'" target="_blank">
            <span class="glyphicon glyphicon glyphicon-new-window"></span>
          </a>
        </div>
      </div>

        <div class="row">
          <div class="col-md-12">
            <div class="h1 text-center">
              Комиссия банка: {{issue.bank_commission}}
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Основные финансовые показатели клиента</div>
              <div class="panel-body">
                <div class="row">
                  <div class="col-md-4 h6">Показатель</div>
                  <div class="col-md-2 h6">Код строки</div>
                  <div class="col-md-2 h6">Последний завершенный квартал</div>
                  <div class="col-md-2 h6">Последний завершенный год</div>
                  <div class="col-md-2 h6">Предыдущий завершенный год</div>
                </div>

                <div class="row">
                  <div class="col-md-4">Валюта баланса</div>
                  <div class="col-md-2">1600</div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1600_offset_0"/>
                  </div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1600_offset_1"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4">Чистые активы</div>
                  <div class="col-md-2">1300</div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1300_offset_0"/>
                  </div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1300_offset_1"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4">Выручка</div>
                  <div class="col-md-2">2110</div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2110_offset_0"/>
                  </div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2110_offset_1"/>
                  </div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2110_offset_2"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4">Прибыль</div>
                  <div class="col-md-2">2400</div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2400_offset_0"/>
                  </div>
                  <div class="col-md-2">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2400_offset_1"/>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
        <div class="panel panel-info">
          <div class="panel-heading">Руководитель компании</div>
          <div class="panel-body">
            <div class="row">
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_passport_series'"
                    :label="'Серия паспорта'"
                    v-model="issue.issuer_head_passport_series"
                  ></bs-input>

                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_passport_number'"
                    :label="'Номер паспорта'"
                    v-model="issue.issuer_head_passport_number"
                  ></bs-input>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_passport_issue_date'"
                    :label="'Дата выдачи'"
                    v-model="issue.issuer_head_passport_issue_date"
                  ></bs-input>

                </div>
              </div>
            </div>

            <div class="row">
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_residence_address'"
                    :label="'Адрес прописки'"
                    v-model="issue.issuer_head_residence_address"
                  ></bs-input>

                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_residence_address'"
                    :label="'Кем выдан паспорт'"
                    v-model="issue.issuer_head_passport_issued_by"
                  ></bs-input>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">

                  <bs-input
                    :name="'issuer_head_phone'"
                    :label="'Телефон'"
                    v-model="issue.issuer_head_phone"
                  ></bs-input>

                </div>
              </div>
            </div>


            <div class="row">
              <div class="col-md-4">
                <div class="form-group">
                                  <bs-input
                    :name="'issuer_head_last_name'"
                    :label="'Фамилия'"
                    v-model="issue.issuer_head_last_name"
                                  ></bs-input>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">

                  <bs-input
                    :name="'issuer_head_first_name'"
                    :label="'Имя'"
                    v-model="issue.issuer_head_first_name"
                  ></bs-input>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_middle_name'"
                    :label="'Отчество'"
                    v-model="issue.issuer_head_middle_name"
                  ></bs-input>

                </div>
              </div>

              <div class="col-md-12">
                <div class="form-group">
                  <bs-input
                    :name="'issuer_head_org_position_and_permissions'"
                    :label="'Должность, полномочия'"
                    v-model="issue.issuer_head_org_position_and_permissions"
                  ></bs-input>

                </div>
              </div>
            </div>

          </div>
        </div>
        <div class="panel panel-info">
          <div class="panel-heading">Состав органов правления(при наличии)</div>
          <div class="panel-body">
            <div class="container-fluid">
              <div class="row formset">
                <span class="h4">Коллегиальный исполнительный орган</span>
                <table class="table">
                  <tr>
                    <th class="h6 col-md-6">Наименование участника</th>
                    <th class="h6 col-md-5">ФИО</th>
                    <th class="col-md-1">&nbsp;</th>
                  </tr>
                  <tbody data-formset-body>

                  <tr v-for="item in issue.org_management_collegial">
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_ogrn_name'"
                        :label="''"
                        v-model="item.org_name"
                      ></bs-input>

                    </td>
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_fio'"
                        :label="''"
                        v-model="item.fio"
                      ></bs-input>
                    </td>
                    <td class="h6">
                      <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                        <span class="glyphicon glyphicon-remove text-danger"></span>
                      </button>
                    </td>
                  </tr>
                  </tbody>
                  <tr>
                    <td colspan="8" class="text-center">
                      <button type="button" class="btn btn-primary" data-formset-add>
                        Добавить коллегиальный орган
                      </button>
                    </td>
                  </tr>
                </table>
              </div>
              <div class="row formset">
                <span class="h4">Совет директоров</span>
                <table class="table">
                  <tr>
                    <th class="h6 col-md-6">Наименование участника</th>
                    <th class="h6 col-md-5">ФИО</th>
                    <th class="col-md-1">&nbsp;</th>
                  </tr>
                  <tbody data-formset-body>
                  <tr v-for="item in issue.org_management_directors">
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_ogrn_name'"
                        :label="''"
                        v-model="item.org_name"
                      ></bs-input>

                    </td>
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_fio'"
                        :label="''"
                        v-model="item.fio"
                      ></bs-input>
                    </td>
                    <td class="h6">
                      <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                        <span class="glyphicon glyphicon-remove text-danger"></span>
                      </button>
                    </td>
                  </tr>
                  </tbody>
                  <tr>
                    <td colspan="8" class="text-center">
                      <button type="button" class="btn btn-primary" data-formset-add>
                        Добавить совет директоров
                      </button>
                    </td>
                  </tr>
                </table>
              </div>
              <div class="row formset">
                <span class="h4">Иной орган управления организации</span>
                <table class="table">
                  <tr>
                    <th class="h6 col-md-6">Наименование участника</th>
                    <th class="h6 col-md-5">ФИО</th>
                    <th class="col-md-1">&nbsp;</th>
                  </tr>
                  <tbody data-formset-body>
                  <tr v-for="item in issue.org_management_others">
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_ogrn_name'"
                        :label="''"
                        v-model="item.org_name"
                      ></bs-input>

                    </td>
                    <td class="h6">
                      <bs-input
                        :name="'org_management_collegial_fio'"
                        :label="''"
                        v-model="item.fio"
                      ></bs-input>
                    </td>
                    <td class="h6">
                      <button type="button" class="btn btn-link btn-xs" >
                        <span class="glyphicon glyphicon-remove text-danger"></span>
                      </button>
                    </td>
                  </tr>
                  </tbody>
                  <tr>
                    <td colspan="8" class="text-center">
                      <button type="button" class="btn btn-primary" data-formset-add>
                        Добавить иной орган управления
                      </button>
                    </td>
                  </tr>
                </table>
              </div>
            </div>

          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Бенефициарные владельцы компании</div>
              <div class="panel-body formset">
                <div class="container-fluid">
                  <div class="row">
                    <table class="table">
                      <tbody data-formset-body>
                      <tr v-for="beneficiar in issue.org_beneficiary_owners" data-formset-form>
                        <td class="h6">
                          <div class="row">
                            <div class="col-md-6">
                              <b>ФИО</b>
                              {{ beneficiar.id }}

                              <bs-input v-model="beneficiar.fio"></bs-input>
                            </div>
                            <div class="col-md-6">
                              <b>ИНН/СНИЛС (при наличии)</b>
                              <bs-input v-model="beneficiar.inn_or_snils"></bs-input>
                            </div>
                          </div>
                          <div class="row">
                            <div class="col-md-4">
                              <b>Адрес регистрации</b>
                              <bs-input v-model="beneficiar.legal_address"></bs-input>
                            </div>
                            <div class="col-md-4">
                              <b>Фактический адрес</b>
                              <bs-input v-model="beneficiar.fact_address"></bs-input>
                            </div>
                            <div class="col-md-4">
                              <b>Почтовый адрес</b>
                              <bs-input v-model="beneficiar.post_address"></bs-input>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div class="row">
                            <div class="col-md-1">
                              <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                                <span class="glyphicon glyphicon-remove text-danger"></span>
                              </button>
                            </div>
                          </div>
                        </td>
                      </tr>
                      </tbody>
                      <tr>
                        <td colspan="7" class="text-center">
                          <button type="button" class="btn btn-primary tr-crt" data-formset-add>
                            Добавить бенефициарного владельца
                          </button>
                        </td>
                      </tr>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Кредитные организации, в которых у принципала открыты счета</div>
              <!--<div class="panel-body formset" data-formset-prefix="{{ formset.prefix }}">-->
              <div class="panel-body formset">
                <div class="container-fluid">
                  <div class="row">

                    <table class="table">
                      <tr>
                        <th class="h6 col-md-6"><b>Наименование</b></th>
                        <th class="h6 col-md-5"><b>БИК</b></th>
                        <th class="col-md-1">&nbsp;</th>
                      </tr>
                      <tbody data-formset-body>

                      <tr v-for="bank in issue.org_bank_accounts">
                        <td class="h6">
                          {{ bank.id }}
                          <bs-input v-model="bank.name"></bs-input>
                        </td>
                        <td class="h6">
                          <bs-input v-model="bank.bik"></bs-input>
                        </td>
                        <td class="h6">

                          <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                            <span class="glyphicon glyphicon-remove text-danger"></span>
                          </button>
                        </td>
                      </tr>

                      </tbody>
                      <tr>
                        <td colspan="7" class="text-center">
                          <button type="button" class="btn btn-primary" data-formset-add>
                            Добавить кредитную организацию
                          </button>
                        </td>
                      </tr>
                    </table>

                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Учредители компании</div>
              <div class="panel-body">
                <div class="container-fluid">
                  <div class="row formset">


                    <span class="h4">Физические лица</span>
                    <table class="table">
                      <tr>
                        <th class="h6 col-md-6"><b>ФИО</b></th>
                        <th class="h6 col-md-5"><b>Доля в УК</b></th>
                        <th class="col-md-1">&nbsp;</th>
                      </tr>
                      <tbody data-formset-body>

                      <tr v-for="person in issue.issuer_founders_physical">
                        <td class="h6">
                          {{ person.id }}
                          <bs-input v-model="person.fio"></bs-input>
                        </td>
                        <td class="h6">
                          <bs-input v-model="person.auth_capital_percentage"></bs-input>
                        </td>
                        <td class="h6">

                          <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                            <span class="glyphicon glyphicon-remove text-danger"></span>
                          </button>
                        </td>
                      </tr>

                      </tbody>
                      <tr>
                        <td colspan="8" class="text-center">
                          <button type="button" class="btn btn-primary" data-formset-add>
                            Добавить физическое лицо
                          </button>
                        </td>
                      </tr>
                    </table>

                  </div>

                  <div class="row formset">

                    <span class="h4">Юридические лица</span>
                    <table class="table">
                      <tr>
                        <th class="h6 col-md-6"><b>Наименование</b></th>
                        <th class="h6 col-md-5"><b>Доля в УК</b></th>
                        <th class="col-md-1">&nbsp;</th>
                      </tr>
                      <tbody data-formset-body>

                      <tr v-for="company in issue.issuer_founders_legal">
                        <td class="h6">
                          {{ company.id }}
                          <bs-input v-model="company.name"></bs-input>

                        </td>
                        <td class="h6">
                          <bs-input v-model="company.auth_capital_percentage"></bs-input>

                        </td>
                        <td class="h6">
                          <button type="button" class="btn btn-link btn-xs" data-formset-delete-button>
                            <span class="glyphicon glyphicon-remove text-danger"></span>
                          </button>
                        </td>
                      </tr>

                      </tbody>
                      <tr>
                        <td colspan="7" class="text-center">
                          <button type="button" class="btn btn-primary" data-formset-add>
                            Добавить юридическое лицо
                          </button>
                        </td>
                      </tr>
                    </table>
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

  moment.locale = 'ru';
  let dateformat = 'DD.MM.YYYY';

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
            let val;
            let start = moment(this.issue.bg_start_date, dateformat);
            let end = this.issue.bg_end_date;
            val = 1 + (end.year() - start.year()) * 12 + end.month() - start.month();
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
        data.csrfmiddlewaretoken = this.$cookie.get('csrftoken');
        this.issue = data;
        this.issue.bg_start_date = moment(data.bg_start_date, dateformat);
        this.issue.bg_end_date = moment(data.bg_end_date, dateformat);
        this.issue.bg_commercial_contract_sign_date = moment(data.bg_commercial_contract_sign_date, dateformat);
        this.issue.bg_commercial_contract_end_date = moment(data.bg_commercial_contract_end_date, dateformat);

        this.finance_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 2
        });
        this.legal_documents = jQuery.grep(data.propose_documents, function (n, i) {
          return n.type === 1
        });
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
