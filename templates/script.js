   
    document.addEventListener('DOMContentLoaded', function() {
        // Sample data for pie chart
        var ctx = document.getElementById('healthChart').getContext('2d');
        var healthChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Healthy', 'In Treatment', 'Critical'],
                datasets: [{
                    label: 'Health Overview',
                    data: [50, 30, 20], // Adjusted to sum up to 100%
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });