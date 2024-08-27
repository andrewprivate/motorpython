close all
% Import csv from data.csv, first row are headers
roughdata = csvread('rough.csv', 1, 0);
% Get the x and y values
x = roughdata(:, 1);
y = roughdata(:, 2);

refinedata = csvread('refine.csv', 1, 0);
% Get the x and y values
x2 = refinedata(:, 1);
y2 = refinedata(:, 2);

% Split refine data into parts with 5 point intervals
x2List = {};
y2List = {};
x2Temp = [];
y2Temp = [];
for i = 1:(length(x2) - 1)
    x2Temp = [x2Temp x2(i)];
    y2Temp = [y2Temp y2(i + 1)];
    if mod(i, 5) == 0
        x2List{end+1} = x2Temp;
        y2List{end+1} = y2Temp;
        x2Temp = [];
        y2Temp = [];
    end
end


% Sort the x values
[x, idx] = sort(x);
% Sort the y values
y = y(idx);

% Plot the data
figure
plot(x, y, 'o');
xlabel('Z-position (cm)');
ylabel('Focus score');
title('Focus score during rough focusing');
grid on

% Get a list of 5 colors, color blind friendly
colors = [0 0 0; 0 0.4470 0.7410; 0.8500 0.3250 0.0980; 0.9290 0.6940 0.1250; 0.4940 0.1840 0.5560; 0.4660 0.6740 0.1880];

% Get limits for the plot
minY = min(y2);
maxY = max(y2);
minX = min(x2);
maxX = max(x2);

% Plot the data
for i = 1:length(x2List)
    figure();
    plot(x2List{i}, y2List{i}, '.', 'MarkerSize', 20, 'Color', colors(i, :));

    % Set the limits
    ylim([minY, maxY]);
    xlim([minX, maxX]);

    xlabel('Z-position (cm)');
    ylabel('Focus score');
    title('Focus score during refined focusing scale ' + string(i));
    grid on
end
