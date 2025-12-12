<template>
  <div class="contact-root">
    <h1>Contactez-nous</h1>
    <p>Vous avez une question ou besoin d’assistance ? Envoyez-nous un message.</p>

    <form class="contact-form" @submit.prevent="sendMessage">
      <div>
        <label>Nom</label>
        <input v-model="form.nom" type="text" required />
      </div>
      <div>
        <label>Email</label>
        <input v-model="form.email" type="email" required />
      </div>
      <div>
        <label>Message</label>
        <textarea v-model="form.message" rows="5" required></textarea>
      </div>
      <button type="submit">Envoyer</button>
    </form>

    <p v-if="success" class="success">Votre message a été envoyé avec succès ✅</p>
    <p v-if="error" class="error">Erreur : {{ error }}</p>
  </div>
</template>

<script>
export default {
  name: "Contact",
  data() {
    return {
      form: { nom: "", email: "", message: "" },
      success: false,
      error: ""
    }
  },
  methods: {
    async sendMessage() {
      try {
        // Exemple : appel API
        console.log("Message envoyé :", this.form)
        this.success = true
        this.error = ""
        this.form = { nom: "", email: "", message: "" }
      } catch (e) {
        this.error = "Impossible d’envoyer le message"
      }
    }
  }
}
</script>

<style src="/css/contact.css"></style>
