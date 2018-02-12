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
                  <a class="list-group-item" href="#/cabinet/requests/70">Сведения о заявлении</a>
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
              <a class="list-group-item" href="#/cabinet/requests/70">Сведения о заявлении</a>
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
                  <div class="col-md-6">Валюта баланса</div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1600_offset_1"/>
                  </div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1600_offset_0"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">Чистые активы</div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1300_offset_1"/>
                  </div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_1300_offset_0"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">Выручка</div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2110_offset_1"/>
                  </div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2110_offset_0"/>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">Прибыль</div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2400_offset_1"/>
                  </div>
                  <div class="col-md-3">
                    <input class="form-control input-sm" type="text" v-model="issue.balance_code_2400_offset_0"/>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-12">
            <div class="panel panel-info">
              <div class="panel-heading">Документация по заявке</div>
              <div class="panel-body">
                <div class="row">
                  <div class="col-md-3">
                    <div class="alert alert-info text-center">
                      <div class="h3">Заявление<br>клиента</div>
                      <a href="" class="btn">Скачать</a>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="alert alert-warning text-center">
                      <div class="h3">Заключение<br>УРДО</div>
                      <a href="" class="btn">Скачать</a>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="alert alert-warning text-center">
                      <div class="h3">Заключение<br>ДБ</div>
                      <a href="" class="btn">Скачать</a>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="alert alert-warning text-center">
                      <div class="h3">Заключение<br>ПУ</div>
                      <a href="" class="btn">Скачать</a>
                    </div>
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
      jQuery.getJSON('http://localhost:8000/rest/issue/' + this.$route.params.id + '?format=json', (data, status, xhr) => {
        this.issue = data
      })
    },

    methods: {
      save_isue: function () {
        jQuery.post('http://localhost:8000/rest/issue/' + this.$route.params.id, this.issue, (data, status, xhr) => {
          this.issue = data
        })
      }
    }
  }
</script>
