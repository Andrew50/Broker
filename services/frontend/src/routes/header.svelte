
<script>
  import { goto } from "$app/navigation";

  function navigateTo(page) {
    goto(page);
  }
</script>


<header class="header">
  <div class="left">
    <a href="/home" on:click={() => navigateTo('/')} class="logo">EdgeFinder</a>
    <a href="/services" on:click={() => navigateTo('/services')}>Services</a>
    <a href="/about" on:click={() => navigateTo('/about')}>About</a>
    <a href="/plans" on:click={() => navigateTo('/plans')}>Plans</a>
  </div>
  <div class="right">
    <a href="/login" on:click={() => navigateTo('/login')}>Log In</a>
    <a href="/signup" on:click={() => navigateTo('/signup')}>Get Started</a>
  </div>
</header>


<style>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    background-color: #007bff; /* Example header background color */
    color: white;
    position: fixed;
    top: 0;
    width: 100%;
    height: 60px;
    z-index: 1000;
  }

  .header .left, .header .right {
    display: flex;
    align-items: center;
  }

  .header a {
    color: white;
    text-decoration: none;
    margin-right: 20px;
    font-size: 16px;
  }
</style>
