<template>
    <v-footer color="primary" padless class="jmelzacki-footer">
            <div class="website-links jmelzacki-policies">
                <div>
                    <h2>
                        Policies
                    </h2>
                </div>
                <div>
                    <router-link to="/terms" class="footer-link">
                        Terms of Service
                    </router-link>
                </div>
                <div>
                    <router-link to="/privacy" class="footer-link">
                        Privacy Policy
                    </router-link>
                </div>
                <div>
                    <router-link to="/cookie" class="footer-link">
                        Cookie Policy
                    </router-link>
                </div>
            </div>
            <div class="website-links jmelzacki-website-links">
                <div>
                    <h2>
                        Website
                    </h2>
                </div>
                <div>
                    <router-link to="/portfolio" class="footer-link">
                        Portfolio
                    </router-link>
                </div>
                <div>
                    <router-link to="/aboutme" class="footer-link">
                        About Me
                    </router-link>
                </div>
            </div>

            <!-- Footer Text -->
            <div class="white--text text-center mt-4 jmelzacki-footnote">
                &copy; {{ new Date().getFullYear() }} JMelzacki
            </div>

            <span class="app-version">
                v{{ config.version }}
            </span>
    </v-footer>
</template>

<script>
import config from '../config.json'

export default {
    name: 'FooterComponent',
    setup() {
        return {
            config
        }
    }
};
</script>

<style scoped>
.v-footer {
    background-color: #1e1e1e !important;
    /* Primary Color (you can change this) */
    display: grid;
    grid-template-rows: auto auto;
    grid-auto-columns: 200px 200px auto;
    align-items: start;
    padding: 5px 30px;
    font-size: 12px;
}

.footer-link {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.footer-link:hover {
    color: #ffeb3b;
    /* Change color on hover */
}

.website-links {
    width: max-content;
}
.jmelzacki-policies {
    grid-column: 1;
}
.jmelzacki-website-links {
    grid-column: 2;
}
.jmelzacki-footnote {
    grid-column: 1 / 4;
}

.app-version {
    position: absolute;
    right: 0px;
    bottom: 0px;
    font-size: 14px;
    opacity: 0.4;
}

@media (max-width: 800px) {
    .v-footer {
        grid-template-rows: auto auto auto;
        grid-auto-columns: 200px auto;
    }
    .jmelzacki-footnote {
        grid-column: 1 / 3;
    }
    .app-version {
        grid-column: 1 / 3;
    }
}
</style>