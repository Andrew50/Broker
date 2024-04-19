
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
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    background-color: var(--c1); /* Example header background color */
    color: var(--f1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 10vh;
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
