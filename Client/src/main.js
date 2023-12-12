import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import "vuetify/dist/vuetify.min.css";
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createApp } from 'vue'
import App from './App.vue'


const vuetify = createVuetify({
    components,
    directives,
  })

createApp(App).use(vuetify).mount('#app') 