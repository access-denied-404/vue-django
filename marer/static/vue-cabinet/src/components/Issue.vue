<template>
  <div class="container">
    <div class="row">
      <h1 class="text-center">Заявка №{{issue.id}}</h1>
      <!--<div class="h4 text-center"><b>Банковская гарантия</b>-->
        <!--на сумму <b>16 000,00 руб.</b>-->
      <!--</div>-->
    </div>
    <div class="row">
      <div class="col-md-3">
        <div class="visible-md visible-lg container" data-spy="affix">
          <div class="row">
            <div class="col-md-3">
              <div class="panel panel-default">
                <div class="list-group">
                  <a class="list-group-item" :href="'#/cabinet/issues/' + issue.id">Сведения о заявлении</a>
                </div>
              </div>
              <div style="margin-top: 30px;">
                <a href="#/cabinet/issues" style="margin-left: 15px;">Вернуться в личный кабинет</a>
              </div>
            </div>
          </div>
        </div>
        <div class="visible-sm visible-xs">
          <div class="h4 text-center text-primary">Этапы прохождения заявки</div>
          <div class="panel panel-default">
            <div class="list-group">
              <a class="list-group-item" :href="'#/cabinet/issues/' + issue.id">Сведения о заявлении</a>
            </div>
          </div>
          <div style="margin-top: 30px;">
            <a href="#/cabinet/issues" style="margin-left: 15px;">Вернуться в личный кабинет</a>
          </div>
        </div>
      </div>
      <div class="col-md-9">
        <div class="row">
            <div class="col-md-12">
              <div class="panel panel-info">
                  <div class="panel-heading">Сведения о заявлении</div>
                  <div class="panel-body">
                    <div class="container-fluid">
                      <div class="row">
                        <div class="col-md-9">
                          <div class="form-group">
                            <label>Компания-заявитель (принципал)</label>
                            <input class="form-control" type="text" v-model="issue.issuer_full_name"/>
                          </div>
                        </div>
                        <div class="col-md-3">
                          <div class="form-group">
                            <label>ИНН</label>
                            <input class="form-control" type="text" v-model="issue.issuer_inn"/>
                          </div>
                        </div>
                      </div>
                      <div class="row">
                        <div class="col-md-4">
                          <div class="form-group">
                            <label>Сумма БГ</label>
                            <input class="form-control" type="number" v-model="issue.bg_sum"/>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
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

        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Заключение УРДО</div>
              <div class="panel-body">

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_all_bank_liabilities_less_than_max"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Лимит на Принципала (группу взаимосвязанных Заемщиков) ВСЕХ обязательств Банка менее 18 000 000 руб
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_executed_contracts_on_44_or_223_or_185_fz"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Клиент исполнил не менее 1 контракта в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ (615 ПП)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_executed_goverment_contract_for_last_3_years"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие исполненного государственного контракта за последние 3 года
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_contract_has_prepayment"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Контракт предусматривает выплату аванса
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_executed_contracts_with_comparable_advances"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Клиент исполнял контракты с авансами сопоставимого или большего размера (допустимое отклонение в меньшую сторону не более 50 % включительно)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Факт исполнения не менее 5 контрактов, заключенных в рамках законов № 44-ФЗ (включая № 94-ФЗ), 223-ФЗ, 185-ФЗ (615 ПП)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Выручка Клиента за последний завершенный год не менее, чем в 5 раз превышает сумму запрашиваемой и действующих в Банке гарантий
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_has_garantor_for_advance_related_requirements"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие Поручителя юридического лица удовлетворяющим одному из предыдущих трех условий
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_contract_price_reduction_lower_than_50_pct_on_supply_contract"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Снижение цены Контракта менее 50% если предмет контракта «Поставка»
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_positive_security_department_conclusion"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие положительного Заключения СБ
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_positive_lawyers_department_conclusion"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие положительного Заключения ПУ (в соответствии с Приказом по проверке ПУ)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов Клиента
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов Клиента
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_need_to_check_real_of_issuer_activity"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Есть необходимость оценки реальности деятельности
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_real_of_issuer_activity_confirms"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Реальность деятельности подтверждается
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right" v-model="issue.is_contract_corresponds_issuer_activity"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Контракт соответствует профилю деятельности клиента
                    </label>
                  </div>
                </div>

                <!-- only big conclusion fields -->
                <div v-if="this.issue.bg_sum >= 1500000">
                  <div class="row">
                    <div class="col-md-1">
                      <input type="checkbox" class="form-control pull-right" v-model="issue.contract_advance_requirements_fails"/>
                    </div>
                    <div class="col-md-11">
                      <label>
                        Не выполняются требования к авансированию (при наличии в контракте аванса)
                      </label>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-1">
                      <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_has_bad_credit_history"/>
                    </div>
                    <div class="col-md-11">
                      <label>
                        Наличие текущей просроченной ссудной задолженности и отрицательной кредитной истории в кредитных организациях
                      </label>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-1">
                      <input type="checkbox" class="form-control pull-right" v-model="issue.is_issuer_has_blocked_bank_account"/>
                    </div>
                    <div class="col-md-11">
                      <label>
                        Наличие информации о блокировке счетов
                      </label>
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
            <button class="btn btn-primary" type="button" v-on:click="save_isue">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
    <br/>
  </div>
</template>

<script>
  import jQuery from 'jquery'
  export default {
    name: 'issue',
    props: ['id'],
    data () {
      return {issue: {}}
    },
    mounted: function () {
      if (window.debug) {
        jQuery.getJSON('http://localhost:8000/rest/issue/' + this.$route.params.id + '?format=json', (data, status, xhr) => {
          data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
          this.issue = data
        })
      } else {
        jQuery.getJSON('/rest/issue/' + this.$route.params.id + '?format=json', (data, status, xhr) => {
          data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
          this.issue = data
        })
      }
    },

    methods: {
      save_isue: function () {
        if (window.debug) {
          jQuery.post('http://localhost:8000/rest/issue/' + this.$route.params.id, this.issue, (data, status, xhr) => {
            data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
            this.issue = data
          })
        } else {
          jQuery.post('/rest/issue/' + this.$route.params.id, this.issue, (data, status, xhr) => {
            data.csrfmiddlewaretoken = this.$cookie.get('csrftoken')
            this.issue = data
          })
        }
      }
    }
  }
</script>
