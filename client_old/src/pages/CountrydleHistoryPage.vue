<template>
    <div class="countrydle-history">
        <v-card class="daily-countrydle">
            <v-card-title style="padding-bottom: 0px; padding-left: 20px; padding-top: 10px;">
                <h3>Daily Countrydle</h3>
            </v-card-title>
            <v-data-table style="padding-top: 0px !important;"
                :items-per-page-options="[5, 10, 20, 50, 100]" :headers="dailyCountriesHeaders"
                :items="countrydle.countrydleHistory">
                <template v-slot:item.index="{ index }">
                    {{ index + 1 }}
                </template>
            </v-data-table>
        </v-card>
        <v-card class="countries-count">
            <v-card-title style="padding-bottom: 0px; padding-left: 20px; padding-top: 10px;">
                <h3>Countries</h3>
            </v-card-title>
            <v-data-table class="my-data-table" style="padding-top: 0px !important; font-size: 12px;"
                :items-per-page-options="[5, 10, 20, 50, 100]" :headers="countriesCountHeaders"
                :items="countrydle.countriesCount">
                <template v-slot:item.index="{ index }">
                    {{ index + 1 }}
                </template>
            </v-data-table>
        </v-card>
    </div>
</template>

<script lang="ts">
import { onMounted } from 'vue';
import { useCountrydleStore } from '../stores/countrydle';

export default {
    name: 'CountrydleHistoryPage',
    setup() {
        const countrydle = useCountrydleStore();
        const dailyCountriesHeaders = [
            { title: 'Index', value: 'index', sortable: false, width: "50px" },
            { title: 'Date', value: 'date', sortable: true, width: "150px" },
            { title: 'Country', value: 'country.name' }
        ];
        const countriesCountHeaders = [
            { title: 'Index', value: 'index', sortable: false },
            { title: 'Country', value: 'name', width: "150px" },
            { title: 'Count', value: 'count', sortable: true },
            { title: 'Last time', value: 'last', sortable: true, width: "200px" },

        ];
        onMounted(() => {
            countrydle.getCountrydleHistory();
        });

        const handleItmesPerPage = (value: number) => {
            console.log(value);
        }

        return {
            countrydle,
            dailyCountriesHeaders,
            countriesCountHeaders,
            handleItmesPerPage
        }
    }
};
</script>

<style scoped>
.countrydle-history {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 15px;
    row-gap: 15px;
}

@media (max-width: 600px) {
    .countrydle-history {
        grid-template-columns: auto;
        grid-template-rows: repeat(2, auto);
    }
    
    .my-data-table {
        font-size: 11px !important;
    }
}
</style>