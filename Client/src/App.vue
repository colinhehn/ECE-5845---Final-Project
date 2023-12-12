<template>
  <div class="main-div">
    <v-tabs v-model="tab" bg-color="primary" @click="reset">
      <v-tab value="one">Query 1</v-tab>
      <v-tab value="two">Query 2</v-tab>
    </v-tabs>
    <div class="header-container">
      <v-window v-model="tab">
        <v-window-item value="one" class="query-one">
          <h1>Top 10 jobs based on a your inputted preferences</h1>
          <h2>Please select your preferred country</h2>
          <v-autocomplete v-model="selectedCountry" label="Input Country" :items="countries"
            @blur="submitCountry"></v-autocomplete>
          <h2 v-if="this.selectedCountry">Please select your preferred city</h2>
          <v-autocomplete v-model="selectedCity" v-if="this.selectedCountry" label="Input City" :items="cities"
            @blur="submitCity"></v-autocomplete>
          <h2 v-if="this.selectedCity">Please select your preferred sector</h2>
          <v-autocomplete v-model="selectedSector" v-if="this.selectedCity" label="Input Sector"
            :items="sectors"></v-autocomplete>
          <h2 v-if="this.selectedSector">Please rank these company traits (top being highest priority)</h2>
          <draggable v-if="this.selectedSector" class="draggable-container" :list="list" @change="log">
            <div class="draggable-text-container" v-for="element, index in list" :key="element.name">
              <p>{{ index + 1 }}. {{ element.name }}</p>
            </div>
          </draggable>
          <v-btn v-if="this.selectedSector" @click="calculatePostgreSQLQuery"
            style="margin-top: 2.5vh; margin-bottom: 5vh;" color="deep-purple-darken-2">Submit</v-btn>
          <v-table fixed-header height="50vh" style="margin-bottom: 25vh;" v-if="returnData">
            <thead>
              <tr>
                <th class="text-left">
                  Job Title
                </th>
                <th class="text-left">
                  Company Name
                </th>
                <th class="text-left">
                  Company Size
                </th>
                <th class="text-left">
                  Salary Type
                </th>
                <th class="text-left">
                  Average Salary
                </th>
                <th class="text-left">
                  Top 10% Salary
                </th>
                <th class="text-left">
                  Bottom 10% Salary
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in returnData" :key="item.id">
                <td>{{ item.job_title }}</td>
                <td>{{ item.company_name }}</td>
                <td>{{ item.company_size }}</td>
                <td>{{ item.salary_type }}</td>
                <td>{{ item.fifty_percentile_salary }}</td>
                <td>{{ item.ninety_percentile_salary }}</td>
                <td>{{ item.ten_percentile_salary }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-window-item>
        <v-window-item value="two" class="query-one">
          <h1>Find similar companies</h1>
          <h2>Please select your preferred country</h2>
          <v-autocomplete v-model="selectedCountry" label="Input Country" :items="countries"
            @blur="submitCountry"></v-autocomplete>
          <h2 v-if="this.selectedCountry">Please select your preferred city</h2>
          <v-autocomplete v-model="selectedCity" v-if="this.selectedCountry" label="Input City" :items="cities"
            @blur="submitCity"></v-autocomplete>
          <h2 v-if="this.selectedCity">Please select your preferred sector</h2>
          <v-autocomplete v-model="selectedSector" v-if="this.selectedCity" label="Input Sector" :items="sectors"
            @blur="grabCompanies"></v-autocomplete>
          <h2 v-if="this.selectedSector">Find a similar company based on this company</h2>
          <v-autocomplete v-model="selectedCompany" v-if="this.selectedSector" label="Input Company"
            :items="companyNames"></v-autocomplete>
          <v-btn v-if="this.selectedCompany" @click="calculate2ndPostgreSQLQuery"
            style="margin-top: 2.5vh; margin-bottom: 5vh;" color="deep-purple-darken-2">Submit</v-btn>
          <h2 v-if="this.returnData">Similar companies</h2>
          <v-table fixed-header height="50vh" style="margin-bottom: 25vh;" v-if="returnData">
            <thead>
              <tr>
                <th class="text-left">
                  Company
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in returnData" :key="index">
                <td>{{ item }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-window-item>
      </v-window>
    </div>
  </div>
</template>
<script>
import { defineComponent } from 'vue'
import { VueDraggableNext } from 'vue-draggable-next'
export default defineComponent({
  components: {
    draggable: VueDraggableNext,
  },
  data() {
    return {
      tab: null,
      enabled: true,
      list: [
        { name: 'Potential Opportunities', id: 'opportunities_ranking' },
        { name: 'Compensation/Benefits', id: 'comp_benefits_ranking' },
        { name: 'Culture/Values', id: 'culture_values_ranking' },
        { name: 'Senior Management', id: 'senior_management_ranking' },
        { name: 'Worklife Balance', id: 'worklife_balance_ranking' },
        { name: 'CEO Approval', id: 'ceo_approval_ranking' },
        { name: 'Company Outlook', id: 'company_outlook_ranking' },
      ],
      jsonList: {
        "opportunities_ranking": 1,
        "comp_benefits_ranking": 2,
        "culture_values_ranking": 3,
        "senior_management_ranking": 4,
        "worklife_balance_ranking": 5,
        "ceo_approval_ranking": 6,
        "company_outlook_ranking": 7,
      },
      countries: [],
      cities: [],
      sectors: [],
      companies: [],
      companyNames: [],
      dragging: false,
      returnData: null,
      selectedCountry: null,
      selectedCity: null,
      selectedSector: null,
      selectedCompany: null,

    }
  },
  methods: {
    log(event) {
      this.jsonList = this.list.reduce((obj, item, index) => {
        obj[item.id] = index + 1;
        return obj;
      }, {});
    },
    submitCountry() {
      this.selectedCity = null
      this.selectedSector = null
      if (this.selectedCountry != null) {
        var requestOptions = {
          method: 'GET',
          redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/cities/distinct/" + this.selectedCountry, requestOptions)
          .then(response => response.json())
          .then(result => {
            this.cities = result.map(city =>
              city.split(' ')
                .map(word =>
                  word.length === 2 ? word.toUpperCase() :
                    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                )
                .join(' ')
            );
            this.cities.push("No Preference");
          })
          .catch(error => console.log('error', error));


      }
    },
    submitCity() {
      this.selectedSector = null
      if (this.selectedCity == "No Preference") {
        this.selectedCity = null
      }
      else {
        var requestOptions = {
          method: 'GET',
          redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/sectors/distinct/" + this.selectedCountry + "/" + this.selectedCity, requestOptions)
          .then(response => response.json())  // Parse the response as JSON
          .then(result => {
            this.sectors = result.map(sector => {
              if (sector === null) {
                return "Other";
              } else {
                return sector.split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                  .join(' ');
              }
            });
          })
          .catch(error => console.log('error', error));


      }
    },
    calculatePostgreSQLQuery() {
      var myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");

      var raw = JSON.stringify({
        "country": this.selectedCountry,
        "city": this.selectedCity,
        "sector": this.selectedSector,
        "ranks": this.jsonList
      });

      var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
      };

      fetch("http://127.0.0.1:5000/similarly/ranked/jobs", requestOptions)
        .then(response => response.json())
        .then(data => {
          // Process each job to handle null values and round salaries
          const processedJobs = data.jobs.map(job => {
            Object.keys(job).forEach(key => {
              if (job[key] === null) {
                job[key] = 'NA'; // Replace null with 'NA'
              } else if (typeof job[key] === 'number') {
                job[key] = parseFloat(job[key].toFixed(2)); // Round numbers to 2 decimal places
              }
            });
            return job;
          });

          this.returnData = processedJobs;
        })
        .catch(error => console.log('error', error));

    },
    reset() {
      this.cities = []
      this.sectors = []
      this.returnData = null
      this.selectedCountry = null
      this.selectedCity = null
      this.selectedSector = null
    },
    grabCompanies() {
      var requestOptions = {
        method: 'GET',
        redirect: 'follow'
      };

      fetch("http://127.0.0.1:5000/company/" + this.selectedCountry + "/" + this.selectedCity + "/" + this.selectedSector, requestOptions)
        .then(response => response.json()) // Parse the response as JSON
        .then(data => {
          this.companies = data.companies; // Assign the company data to this.companies
          this.companyNames = data.companies.map(company => company.name); // Extract company names
          console.log(this.companyNames); // Log company names to the console for verification
        })
        .catch(error => console.log('error', error));



    },
    calculate2ndPostgreSQLQuery() {
      let company = this.companies.find(c => c.name === this.selectedCompany);
      console.log(company.id)
      var requestOptions = {
        method: 'GET',
        redirect: 'follow'
      };

      fetch("http://127.0.0.1:5000/similar/companies/" + company.id + "/" + this.selectedCountry + "/" + this.selectedCity, requestOptions)
        .then(response => response.json()) // Parse the response as JSON
        .then(data => {
          this.returnData = data.companies.map(company => company.name); // Extract and assign company names
          console.log(this.returnData); // Log the company names to the console for verification
        })
        .catch(error => console.log('error', error));


    }
  },
  async created() {
    //Grab list of countries from backend and set to dropdown
    var requestOptions = {
      method: 'GET',
      redirect: 'follow',
      headers: {
        'Content-Type': 'application/json',
      }
    };

    fetch("http://127.0.0.1:5000/countries/distinct", requestOptions)
      .then(response => response.json()) // Assuming the response is in JSON format
      .then(result => {
        this.countries = result.map(country =>
          country.split(' ').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
          ).join(' ')
        );
      })
      .catch(error => console.log('error', error));

  },
})
</script>

<style>
.draggable-container {
  font-size: 1.5em;
  margin-bottom: 5vh;
}

.header-container {
  max-width: 65vw;
  outline: solid;
  margin: 2.5vh auto;
}

.draggable-text-container {
  background-color: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  margin: 10px;
  cursor: move;
}

.main-div {
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background-color: white;
}

h1 {
  font-size: 2em;
  padding: 1em;
}

h2 {
  font-size: 1.5em;
  margin-top: 5vh;
}

.query-one {
  padding: 1em;
}
</style>