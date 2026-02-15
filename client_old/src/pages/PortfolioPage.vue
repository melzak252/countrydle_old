<template>
  <v-container class="my-10">
    <v-row class="justify-center">
      <v-col cols="12" md="8">
        <v-card elevation="10" class="pa-5">
          <v-card-title class="headline font-weight-bold ">
            How I Built This Website            
          </v-card-title>
          <v-card-text class="py-5">
            <div class="timeline">
              <v-timeline density="compact">
                <v-timeline-item v-for="(item, index) in completedItems" :key="index" :color="item.color" small
                  size="30px" class="timeline-card">
                  <v-card flat d>
                    <v-card-title class="timeline-card-title">{{ item.title }}</v-card-title>
                    <v-card-subtitle class="timeline-card-subtitle">{{ item.subtitle }}</v-card-subtitle>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </div>
            <div class="timeline">
              <h2 class="text-h8 font-weight-medium mb-4 timeline-title">
                Future improvements
              </h2>
              <v-timeline density="compact">
                <v-timeline-item v-for="(item, index) in plannedItems" :key="index" :color="item.color" size="30px"
                  class="timeline-item-elem">
                  <v-card flat>
                    <v-card-title class="timeline-card-title">{{ item.title }}</v-card-title>
                    <v-card-subtitle class="timeline-card-subtitle">{{ item.subtitle }}</v-card-subtitle>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">

export default {
  name: 'PortfolioPage',
  setup() {

  },
  data() {
    return {
      completedItems: [
        { title: "Idea for the Game", subtitle: "Conceptualized the game", color: "teal" },
        { title: "Creating API in FastAPI", subtitle: "Developed backend API using FastAPI", color: "green" },
        { title: "Adding PostgreSQL Database", subtitle: "Integrated PostgreSQL for data storage", color: "blue" },
        { title: "OpenAI Integration", subtitle: "Incorporated OpenAI for main game functionality", color: "red" },
        { title: "Creating Frontend in Vue3.ts", subtitle: "Developed the frontend using Vue 3 and TypeScript", color: "orange" },
        { title: "Containerization with Docker", subtitle: "Containerized all services using Docker Compose, managed by an Nginx container", color: "purple" },
        { title: "Hosting on Linode", subtitle: "Deployed on a Debian 11 server at Linode", color: "brown" },
        { title: "Qdrant RAG Enhancing", subtitle: "Integrate Qdrant to enhance data retrieval for creating context for country quiz ", color: "cyan" },
        { title: "Add Email Verification", subtitle: "Implement email verification for new users", color: "light-green" },
      ],
      plannedItems: [
        { title: "More Visual Updates", subtitle: "Plan for ongoing improvements in UI/UX", color: "pink" }
      ]
    };
  }
};
</script>

<style scoped>
.timeline-card-subtitle {
  text-wrap: wrap;
  width: 100%;
  padding-right: 15px;
}


.timeline-title {
  text-align: center;
  padding-right: 2rem;
}

@media (max-width: 500px) {
  .timeline-item-elem {
    width: 100%;
  }

  .timeline-card-title {
    font-size: small;
    text-wrap: wrap;
    padding: 5px;
    width: 100%;
  }

  .timeline-card-subtitle {
    display: none;
  }


  .timeline-title {
    text-align: left;
  }


}
</style>

<style>
.v-timeline--vertical.v-timeline .v-timeline-item:nth-child(2n) .v-timeline-item__body {
  grid-column: 3 !important;
}

.v-timeline-item__opposite {
  display: none;
}

.v-timeline-item__body {
  padding-left: 1.5rem;
  text-align: left;
  /* Align text to the left */
}


.v-timeline-item .v-card-title,
.v-timeline-item .v-card-subtitle,
.v-timeline-item .v-card-text {
  text-align: left;
  /* Ensure all text in cards is left-aligned */
}

.timeline {
  display: flex;
  flex-direction: column;
  align-items: start;
}
</style>