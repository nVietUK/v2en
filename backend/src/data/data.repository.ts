import { Injectable } from '@nestjs/common';
import { DataSource, Repository } from 'typeorm';
import { Data } from './data.entity';

@Injectable()
export class DataRepository extends Repository<Data> {
	constructor(
		private dataSource: DataSource = new DataSource({
			connectorPackage: 'mysql2',
			type: 'mysql',
		}),
	) {
		super(Data, dataSource.createEntityManager());
	}

	async All(): Promise<Data[]> {
		return await this.dataSource
			.getRepository(Data)
			.createQueryBuilder()
			.getMany();
	}

	async findOneByID(id: number): Promise<Data | null> {
		return await this.dataSource.getRepository(Data).findOneBy({ id: id });
	}

	async findOneByHashValue(hashValue: string): Promise<Data | null> {
		return await this.dataSource
			.getRepository(Data)
			.findOneBy({ hashValue: hashValue });
	}

	async findAll(): Promise<Data[]> {
		return await this.dataSource.getRepository(Data).find();
	}
}
