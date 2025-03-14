<template>  
  <div id="app">  
    <ChatWindows />  
  </div>  
</template>  
  
<script>  
import ChatWindows from './components/ChatWindows.vue';  
  
export default {  
  name: 'App',  
  components: {  
    ChatWindows
  }  
};  
</script>  
  
<style>  
#app {  
  font-family: 'Avenir', Helvetica, Arial, sans-serif;  
  -webkit-font-smoothing: antialiased;  
  -moz-osx-font-smoothing: grayscale;  
  text-align: center;  
  color: #2c3e50;  
  margin-top: 60px;  
}  
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>  
