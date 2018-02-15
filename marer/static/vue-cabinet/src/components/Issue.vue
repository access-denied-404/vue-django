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
        <div class="panel panel-info">
          <div class="panel-heading">
            Состав органов правления(при наличии)
          </div>
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
              <div class="panel-body formset" data-formset-prefix="{{ formset.prefix }}">
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
              <div class="panel-heading">Документы</div>
              <div class="panel-body">
                <div class="row">
                  <div class="col-md-12">
                    <table class="table table-condensed">
                      <tr class="application_doc" v-if="issue.application_doc">
                        <td class="h6">
                          <a href="{{ issue.application_doc.file }}">
                            <b>Заявление на предоставление банковской гарантии</b>
                          </a>
                          <div class="clearfix"></div>
                        </td>
                      </tr>
                      <tr v-if="finance_documents">
                        <td>
                          <h4 style="font-weight: bold;">Финансовые документы</h4>
                        </td>
                      </tr>
                      <tr v-for="doc in finance_documents">
                        <td class="h6">
                          <a v-if="doc.document.file" href="{{ doc.document.file }}">{{ doc.name }}</a>
                          <div v-if="!doc.document.file">
                            {{ doc.name }} <span v-if="doc.is_required" class="text-danger"><b>*</b></span>
                          </div>
                          <div class="pull-right">
                            <div class="row" v-if="!doc.document.file">
                              <div class="form-group">
                                <div class="col-md-10">
                                  <input type="file" name="propose_doc_{{ doc.id }}"
                                         v-bind:class="{'required': doc.is_required}" class="input-sm pull-right"/>
                                </div>
                                <div class="col-md-2">
                                  <span class="glyphicon glyphicon-ok text-success hidden to-hide"></span>
                                </div>
                              </div>
                            </div>
                            <button v-if="issue.status == 'registering'" type="submit"
                                    class="btn btn-link btn-xs pull-right" form="propose_doc_{{ doc.id }}_del_form">
                              <span class="glyphicon glyphicon-remove text-danger"></span>
                            </button>
                            <div class="clearfix"></div>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="legal_documents">
                        <td>
                          <h4 style="font-weight: bold;">Юридические документы</h4>
                        </td>
                      </tr>
                      <tr v-for="doc in legal_documents">
                        <td class="h6">
                          <a v-if="doc.document.file" href="{{ doc.document.file }}">{{ doc.name }}</a>
                          <div v-if="!doc.document.file">
                            {{ doc.name }} <span v-if="doc.is_required" class="text-danger"><b>*</b></span>
                          </div>
                          <div class="pull-right">
                            <div class="row" v-if="!doc.document.file">
                              <div class="form-group">
                                <div class="col-md-10">
                                  <input type="file" name="propose_doc_{{ doc.id }}"
                                         v-bind:class="{'required': doc.is_required}" class="input-sm pull-right"/>
                                </div>
                                <div class="col-md-2">
                                  <span class="glyphicon glyphicon-ok text-success hidden to-hide"></span>
                                </div>
                              </div>
                            </div>
                            <button v-if="issue.status == 'registering'" type="submit"
                                    class="btn btn-link btn-xs pull-right" form="propose_doc_{{ doc.id }}_del_form">
                              <span class="glyphicon glyphicon-remove text-danger"></span>
                            </button>
                            <div class="clearfix"></div>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="other_documents">
                        <td>
                          <h4 style="font-weight: bold;">Прочее</h4>
                        </td>
                      </tr>
                      <tr v-for="doc in other_documents">
                        <td class="h6">
                          <a v-if="doc.document.file" href="{{ doc.document.file }}">{{ doc.name }}</a>
                          <div v-if="!doc.document.file">
                            {{ doc.name }} <span v-if="doc.is_required" class="text-danger"><b>*</b></span>
                          </div>
                          <div class="pull-right">
                            <div class="row" v-if="!doc.document.file">
                              <div class="form-group">
                                <div class="col-md-10">
                                  <input type="file" name="propose_doc_{{ doc.id }}"
                                         v-bind:class="{'required': doc.is_required}" class="input-sm pull-right"/>
                                </div>
                                <div class="col-md-2">
                                  <span class="glyphicon glyphicon-ok text-success hidden to-hide"></span>
                                </div>
                              </div>
                            </div>
                            <button v-if="issue.status == 'registering'" type="submit"
                                    class="btn btn-link btn-xs pull-right" form="propose_doc_{{ doc.id }}_del_form">
                              <span class="glyphicon glyphicon-remove text-danger"></span>
                            </button>
                            <div class="clearfix"></div>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="issue.bg_contract_doc || issue.bg_doc || issue.transfer_acceptance_act">
                        <td>
                          <h4 style="font-weight: bold;">Договора и акты</h4>
                        </td>
                      </tr>
                      <tr v-if="issue.bg_contract_doc">
                        <td>
                          <a href="{{ issue.bg_contract_doc.file }}">Договор</a>
                        </td>
                      </tr>
                      <tr v-if="issue.bg_doc">
                        <td>
                          <a href="{{ issue.bg_doc.file}}">Проект</a>
                        </td>
                      </tr>
                      <tr v-if="issue.transfer_acceptance_act">
                        <td>
                          <a href="{{ issue.transfer_acceptance_act.file }}">Акт</a>
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
              <div class="panel-heading">Заключение УРДО</div>
              <div class="panel-body">

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_all_bank_liabilities_less_than_max" type="primary">
                      Лимит на Принципала (группу взаимосвязанных Заемщиков) ВСЕХ обязательств Банка менее 18 000 000 руб
                    </checkbox>

                  </div>
                </div>

                <div class="row">
                  <div class="col-md-12">
                    <checkbox :checked.sync="issue.is_issuer_executed_contracts_on_44_or_223_or_185_fz" type="primary">
                      Клиент исполнил не менее 1 контракта в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ (615 ПП)
                    </checkbox>
                  </div>

                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_issuer_executed_goverment_contract_for_last_3_years"/>
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
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_issuer_executed_contracts_with_comparable_advances"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Клиент исполнял контракты с авансами сопоставимого или большего размера (допустимое отклонение в меньшую сторону не более 50 % включительно)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Факт исполнения не менее 5 контрактов, заключенных в рамках законов № 44-ФЗ (включая № 94-ФЗ), 223-ФЗ, 185-ФЗ (615 ПП)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Выручка Клиента за последний завершенный год не менее, чем в 5 раз превышает сумму запрашиваемой и действующих в Банке гарантий
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_issuer_has_garantor_for_advance_related_requirements"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие Поручителя юридического лица удовлетворяющим одному из предыдущих трех условий
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_contract_price_reduction_lower_than_50_pct_on_supply_contract"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Снижение цены Контракта менее 50% если предмет контракта «Поставка»
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_positive_security_department_conclusion"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие положительного Заключения СБ
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_positive_lawyers_department_conclusion"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Наличие положительного Заключения ПУ (в соответствии с Приказом по проверке ПУ)
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов Клиента
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов Клиента
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_need_to_check_real_of_issuer_activity"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Есть необходимость оценки реальности деятельности
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_real_of_issuer_activity_confirms"/>
                  </div>
                  <div class="col-md-11">
                    <label>
                      Реальность деятельности подтверждается
                    </label>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-1">
                    <input type="checkbox" class="form-control pull-right"
                           v-model="issue.is_contract_corresponds_issuer_activity"/>
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
                      <input type="checkbox" class="form-control pull-right"
                             v-model="issue.contract_advance_requirements_fails"/>
                    </div>
                    <div class="col-md-11">
                      <label>
                        Не выполняются требования к авансированию (при наличии в контракте аванса)
                      </label>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-1">
                      <input type="checkbox" class="form-control pull-right"
                             v-model="issue.is_issuer_has_bad_credit_history"/>
                    </div>
                    <div class="col-md-11">
                      <label>
                        Наличие текущей просроченной ссудной задолженности и отрицательной кредитной истории в кредитных организациях
                      </label>
                    </div>
                  </div>

                  <div class="row">
                    <div class="col-md-1">
                      <input type="checkbox" class="form-control pull-right"
                             v-model="issue.is_issuer_has_blocked_bank_account"/>
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
      'Money': Money
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
