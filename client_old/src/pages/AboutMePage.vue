<!-- src/pages/AboutMePage.vue -->
<template>
  <v-container class="my-10">
    <v-row class="justify-center">
      <v-card elevation="10" class="pa-5">
        <v-card-title class="text-h5 font-weight-bold">
          Jakub Melzacki
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="about-me-body">
            <v-avatar size="300">
              <v-img src="/Jakub_Melzacki.png" alt="Jakub Melzacki"></v-img>
            </v-avatar>
            <div class="text-container">
              <h2 class="text-h5 font-weight-bold mb-4">About Me</h2>
              <p>
                I am a passionate knowledge-seeker. If you have interesting information, I’m always eager to hear it!
                😋 <br>
                My main fields of interest include Physics, Mathematics, Computer Science, and Philosophy (I strongly
                believe Hegel is a charlatan!). <br>
              </p>
              <br>

              <h5 class="text-h5 font-weight-bold mb-4">Currently</h5>
              <p>
                I am focusing on developing my skills in <strong>Data Science</strong>, aiming to apply this knowledge
                to my hobby of creating intelligent systems for games like <strong>League of Legends, TFT,
                  Chess</strong>, and many others. <br>
                <br>
                I serve as the Vice President of the <strong>DataScience Club at PJATK</strong>, where I am recognized
                as an expert in <strong>Python</strong>, the language in which I feel most comfortable.
                However, that doesn’t mean other technologies are foreign to me! <br>
                I also have experience with <strong>C++20, TypeScript, Bash</strong>, and many other tools and
                languages.
              </p>
              <br>
              <p>
                Do you have an exciting project and need versatile support? <strong>I’m your man!</strong>
              </p>
            </div>
          </div>
          <br>
          <v-divider></v-divider>
          <v-row class="my-5 justify-center">
            <v-col cols="12">
              <h3 class="text-h6 font-weight-bold mb-4">Get in Touch:</h3>
              <v-row justify="center" class="mb-4">
                <v-col cols="12" md="4">
                  <v-btn block color="indigo" href="https://github.com/melzak252" target="_blank" large>
                    <v-icon left>mdi-github</v-icon>
                    GitHub
                  </v-btn>
                </v-col>
                <v-col cols="12" md="4">
                  <v-btn block color="blue darken-3" href="https://linkedin.com/in/jmelzacki/" target="_blank" large>
                    <v-icon left>mdi-linkedin</v-icon>
                    LinkedIn
                  </v-btn>
                </v-col>
                <v-col cols="12" md="4">
                  <v-btn block color="purple" large>
                    <v-icon left>mdi-discord</v-icon>
                    Discord: .melzak
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-row>
  </v-container>
</template>

<script lang="ts">
export default {
  name: 'AboutMePage',
};
</script>

<style scoped>
.headline {
  color: #1e88e5;
}

.text-h5 {
  color: #424242;
}

.text-h6 {
  color: #616161;
}

.about-me-body {
  display: grid;
  grid-template-rows: auto;
  justify-content: center;
}

@media (min-width: 800px) {
  .about-me-body {
    display: grid;
    grid-template-columns: 300px auto;
    grid-template-rows: auto;
    justify-content: center;
    column-gap: 20px;
  }
}
</style>
