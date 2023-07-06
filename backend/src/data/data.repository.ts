import { Injectable } from '@nestjs/common';
import { DataSource, Repository } from 'typeorm';
import { Data } from './data.entity';

@Injectable()
export class DataRepository extends Repository<Data> {
	constructor(private dataSource: DataSource) {
		super(Data, dataSource.createEntityManager());
	}
}
