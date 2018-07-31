function out = get_load_on_branch(file)
load(file);
% PF real power injected at from bus end (MW)
PF = 14;
n_intervals = size(mdo.flow,1);
n_branches = size(mdo.flow(1).mpc.branch,1);
out = zeros(n_branches,n_intervals);
for i = (1:n_intervals)
    out(:,i) = mdo.flow(i).mpc.branch(:,PF);
end

end