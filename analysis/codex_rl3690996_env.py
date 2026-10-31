"""Gymnasium wrappers over causal, broker-free research ledgers."""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from codex_rl3690996_core import StockBook, FuturesBook, stock_weights


class StockEnv(gym.Env):
    def __init__(self, data, days, training=False, book=None, cost_multiplier=1., overlay=True):
        self.data=data; self.days=np.asarray(days,int); self.training=training; self.n=data["c"].shape[1]
        self.book=book; self.external_book=book; self.mult=cost_multiplier; self.overlay=overlay
        self.action_space=spaces.Box(-1,1,shape=(self.n,),dtype=np.float32)
        self.observation_space=spaces.Box(-np.inf,np.inf,shape=(1+6*self.n,),dtype=np.float32)

    def _obs(self):
        d=self.active[self.p]-1 if self.p<len(self.active) else self.active[-1]
        equity=self.book.equity(self.data["c"][d])
        return np.r_[self.book.cash/equity, self.book.q*self.data["c"][d]/equity,
                     self.data["features"][d].ravel()].astype(np.float32)

    def reset(self,seed=None,options=None):
        super().reset(seed=seed)
        if self.training:
            length=min(252,len(self.days)); start=int(self.np_random.integers(0,len(self.days)-length+1))
            self.active=self.days[start:start+length]
        else:
            self.active=self.days
        self.p=0; self.book=self.external_book or StockBook(self.n,cost_multiplier=self.mult)
        return self._obs(),{}

    def step(self,action):
        i=self.active[self.p]; d=i-1
        before=self.book.equity(self.data["c"][d])
        weights=stock_weights(action,self.n)
        risk=self.overlay and self.data["score"][d]>self.data["threshold"][d]
        if risk: weights=np.zeros(self.n)
        fees,slip=self.book.fees,self.book.slip
        after=self.book.transition(weights,self.data["c"][d],self.data["o"][i],self.data["c"][i],
                                   self.data["split"][i],self.data["dates"][d],self.data["dates"][i])
        self.p+=1; done=self.p>=len(self.active)
        return self._obs(),float(100*np.log(after/before)),done,False,dict(date=int(self.data["dates"][i]),
            equity=after,net=after-before,fee=self.book.fees-fees,slippage=self.book.slip-slip,
            risk_off=bool(risk),exposure=float(self.book.q@self.data["c"][i]/after))


def futures_target(action):
    a=float(np.asarray(action).ravel()[0])
    return 1 if a>1/3 else (-1 if a<-1/3 else 0)


class FuturesEnv(gym.Env):
    def __init__(self,data,days,training=False,contracts=1,cost_multiplier=1.,overlay=True,log=False):
        self.data=data; self.days=np.asarray(days,int); self.training=training; self.contracts=contracts
        self.mult=cost_multiplier; self.overlay=overlay; self.log=log
        self.action_space=spaces.Box(-1,1,shape=(1,),dtype=np.float32)
        self.observation_space=spaces.Box(-np.inf,np.inf,shape=(12,),dtype=np.float32)

    def _obs(self):
        i=self.day; k=min(self.k,77); px=self.data["c"][i,4+5*k]
        score=self.data["score"][i,k]; threshold=self.data["threshold"][i,k]
        phase=min(k/76,1.)
        return np.r_[self.data["features"][i,k],min(score/max(threshold,1e-9),5.),
            self.book.net/(250*self.contracts), self.book.q/self.contracts,
            (self.book.equity(px)-self.book.net)/(250*self.contracts),
            np.sin(2*np.pi*phase),np.cos(2*np.pi*phase),self.data["atr"][i]/px*100].astype(np.float32)

    def reset(self,seed=None,options=None):
        super().reset(seed=seed)
        self.day=int(self.np_random.choice(self.days)) if self.training else int((options or {}).get("day",self.days[0]))
        if self.day not in self.days: raise ValueError("Episode outside allowed fit/evaluation days")
        self.k=0; self.book=FuturesBook(self.contracts,self.mult,self.log)
        return self._obs(),{}

    def step(self,action):
        i=self.day; k=self.k
        before=self.book.equity(self.data["c"][i,4+5*k])
        target=futures_target(action)
        risk=self.overlay and self.data["score"][i,k]>self.data["threshold"][i,k]
        if risk: target=0
        after=self.book.step(target,*(self.data[x][i] for x in ["o","h","l","c"]),
                             self.data["atr"][i],self.data["dates"][i],k)
        self.k+=1; done=self.k==77
        return self._obs(),float((after-before)/(25*self.contracts)),done,False,dict(
            date=int(self.data["dates"][i]),net=float(self.book.net),adverse=float(self.book.low),
            fee=float(self.book.fees),slippage=float(self.book.slip),risk_off=bool(risk))
