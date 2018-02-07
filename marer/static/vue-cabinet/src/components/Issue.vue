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
                <a href="#/cabinet/requests" style="margin-left: 15px;">Вернуться в личный кабинет</a>
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
            <a href="#/cabinet/requests" style="margin-left: 15px;">Вернуться в личный кабинет</a>
          </div>
        </div>
      </div>
      <div class="col-md-9">
        <form method="post">
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
                            {{issue.issuer_full_name}}
                          </div>
                        </div>
                        <div class="col-md-3">
                          <div class="form-group">
                            <label>ИНН</label>
                            {{issue.issuer_inn}}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
          </div>
        </form>
      </div>
    </div>
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
    }
  }
</script>
