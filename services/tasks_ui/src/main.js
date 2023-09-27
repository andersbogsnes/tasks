import {createApp} from 'vue'
import App from './App.vue'
import {Amplify} from 'aws-amplify';
import awsExports from "./aws-exports.js";
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';


Amplify.configure(awsExports);
const app = createApp(App)
app.use(ElementPlus)

app.mount('#app')
