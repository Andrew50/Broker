

export const GET = ({ request }) => {
    const authHeader = request.headers.get('Authorization')


    if (!authHeader !== 'Myauthheader') {
        return new response(JSON.stringify({ message: 'Invalid credentials' }), {
            status: 401
        })
    }

    const res = await fetch('https://')
    return new Response(JSON.stringify({ message: "Hello" }), { status: 200 })


}