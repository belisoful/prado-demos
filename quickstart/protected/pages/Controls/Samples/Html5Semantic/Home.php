<?php

class Home extends TPage
{
	public function onLoad($param)
	{
		parent::onLoad($param);
		$this->PrimaryNav->getAttributes()->add('aria-label', 'Primary');
		$this->FooterNav->getAttributes()->add('aria-label', 'Footer');
	}
}
