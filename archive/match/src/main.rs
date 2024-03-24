fn derivative(sequence: &[f64]) -> Vec<f64> {
    sequence.windows(2).map(|w| w[1] - w[0]).collect()
}

fn euclidean_distance(a: f64, b: f64) -> f64 {
    (a - b).abs()
}

fn ddtw(sequence1: &[f64], sequence2: &[f64]) -> f64 {
    let derivative1 = derivative(sequence1);
    let derivative2 = derivative(sequence2);

    let m = derivative1.len();
    let n = derivative2.len();
    let mut dp = vec![vec![0.0; n + 1]; m + 1];

    for i in 1..=m {
        dp[i][0] = f64::INFINITY;
    }
    for j in 1..=n {
        dp[0][j] = f64::INFINITY;
    }

    for i in 1..=m {
        for j in 1..=n {
            let cost = euclidean_distance(derivative1[i - 1], derivative2[j - 1]);
            dp[i][j] = cost + dp[i - 1][j - 1].min(dp[i - 1][j].min(dp[i][j - 1]));
        }
    }

    dp[m][n]
}

fn main() {
    let sequence1 = vec![1.0, 2.0, 3.0, 4.0, 5.0];
    let sequence2 = vec![2.0, 3.0, 4.0, 5.0, 6.0];

    let distance = ddtw(&sequence1, &sequence2);
    println!("DDTW Distance: {}", distance);
}
