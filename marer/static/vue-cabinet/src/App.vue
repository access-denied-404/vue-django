<template>
  <div id="app-root">
    <nav class="navbar navbar-default navbar-static-top">
      <div class="container">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                  data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/">
            <img src="/static/marer/img/logo_sgb.png" height="25"/>
          </a>
        </div>
        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <ul class="nav navbar-nav navbar-right">
            <li>
              <a href="/admin/">
                <span class="text-primary">Управление</span>
                <span class="glyphicon glyphicon-briefcase text-primary"></span>
              </a>
            </li>
            <li>
              <a href="/cabinet/requests">
                <span class="text-primary">Владислав Зиминов</span>
                <span class="glyphicon glyphicon-user text-primary"></span>
              </a>
            </li>
            <li><a href="/logout">Выход</a></li>
          </ul>
        </div><!-- /.navbar-collapse -->
      </div><!-- /.container-fluid -->
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
  export default {
    name: 'app',
    data () {}
  }
</script>
